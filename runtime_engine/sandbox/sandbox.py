from __future__ import annotations

import asyncio
import json
import logging
import os
import platform
import shutil
import tempfile
import time
import uuid
from pathlib import Path
from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator

logger = logging.getLogger(__name__)


class SandboxResult(BaseModel):
    exit_code: int
    stdout: str
    stderr: str
    duration_ms: float = 0
    memory_peak_mb: float = 0


class ResourceUsage(BaseModel):
    cpu_time_ms: int = 0
    memory_peak_mb: int = 0
    disk_read_mb: int = 0
    disk_write_mb: int = 0
    network_rx_bytes: int = 0
    network_tx_bytes: int = 0


class SandboxPolicy(BaseModel):
    """Security policy for sandbox execution."""
    
    # Resource limits
    max_memory_mb: int = Field(default=512, ge=64, le=8192)
    max_cpu_seconds: int = Field(default=60, ge=1, le=3600)
    max_disk_mb: int = Field(default=1024, ge=100, le=10240)
    max_processes: int = Field(default=50, ge=10, le=500)
    max_file_size_mb: int = Field(default=100, ge=1, le=1000)
    
    # Network
    network_access: bool = False
    allowed_domains: list[str] = Field(default_factory=list)
    
    # Filesystem
    read_only_paths: list[str] = Field(default_factory=lambda: ["/etc", "/usr", "/bin", "/sbin", "/lib", "/lib64", "/sys", "/proc"])
    read_write_paths: list[str] = Field(default_factory=lambda: ["/tmp", "/workspace"])
    temp_dir_size_mb: int = Field(default=256, ge=10, le=2048)
    
    # Command control
    allowed_commands: list[str] = Field(default_factory=list)
    blocked_commands: list[str] = Field(default_factory=lambda: [
        "rm -rf /", "rm -rf /*", "mkfs", "dd if=/dev/zero", "dd if=/dev/urandom",
        "format", "shutdown", "reboot", "halt", "init", "kill -9 1",
        "wget", "curl", "nc", "ncat", "netcat", "socat",
        "ssh", "scp", "rsync", "ftp", "sftp",
        "mount", "umount", "fdisk", "parted", "cfdisk",
        "systemctl", "service", "systemd",
        "iptables", "ip6tables", "ufw", "firewall-cmd",
        "chmod 777", "chmod -R 777",
        "chown root", "chown -R root",
        "su -", "sudo", "doas",
        "passwd", "usermod", "useradd", "userdel",
        "groupadd", "groupdel", "groupmod",
        "crontab", "at", "batch",
        "dd", "shred", "wipe",
    ])
    
    # Security
    drop_capabilities: list[str] = Field(default_factory=lambda: [
        "CAP_SYS_ADMIN", "CAP_SYS_RESOURCE", "CAP_SYS_MODULE",
        "CAP_SYS_RAWIO", "CAP_SYS_PACCT", "CAP_SYS_NICE",
        "CAP_SYS_TIME", "CAP_SYS_TTY_CONFIG", "CAP_SYSLOG",
        "CAP_DAC_OVERRIDE", "CAP_DAC_READ_SEARCH",
        "CAP_FOWNER", "CAP_FSETID", "CAP_KILL",
        "CAP_SETGID", "CAP_SETUID", "CAP_SETPCAP",
        "CAP_LINUX_IMMUTABLE", "CAP_NET_ADMIN",
        "CAP_NET_BIND_SERVICE", "CAP_NET_BROADCAST",
        "CAP_NET_RAW", "CAP_IPC_LOCK", "CAP_IPC_OWNER",
        "CAP_SYS_CHROOT", "CAP_SYS_PTRACE",
        "CAP_MKNOD", "CAP_LEASE", "CAP_AUDIT_WRITE",
        "CAP_AUDIT_CONTROL", "CAP_SETFCAP",
        "CAP_MAC_OVERRIDE", "CAP_MAC_ADMIN",
        "CAP_SYSLOG", "CAP_WAKE_ALARM",
        "CAP_BLOCK_SUSPEND", "CAP_AUDIT_READ",
    ])
    
    # Seccomp
    seccomp_profile: str = "default"
    custom_seccomp_rules: dict[str, list[str]] = Field(default_factory=dict)
    
    # User namespace
    use_user_namespace: bool = True
    uid_map: str = "0:100000:65536"
    gid_map: str = "0:100000:65536"
    
    # Runtime
    timeout_seconds: int = Field(default=300, ge=1, le=3600)
    execution_log_max_entries: int = Field(default=1000, ge=100, le=10000)

    @field_validator("max_memory_mb")
    @classmethod
    def validate_memory(cls, v: int) -> int:
        # Check available system memory
        try:
            import psutil
            available = psutil.virtual_memory().available // (1024 * 1024)
            if v > available * 0.8:
                logger.warning(f"Memory limit {v}MB exceeds 80% of available {available}MB")
        except ImportError:
            pass
        return v


class Sandbox:
    async def create(self) -> str:
        raise NotImplementedError

    async def execute(self, command: list[str], timeout: int = 30) -> SandboxResult:
        raise NotImplementedError

    async def destroy(self) -> None:
        raise NotImplementedError

    async def get_usage(self) -> ResourceUsage:
        raise NotImplementedError


class DefaultSandbox(Sandbox):
    """Enhanced temp-directory based sandbox with resource limits and monitoring."""

    def __init__(self, policy: SandboxPolicy | None = None) -> None:
        self._policy = policy or SandboxPolicy()
        self._sandbox_id: str | None = None
        self._work_dir: Path | None = None
        self._execution_log: list[dict[str, Any]] = []
        self._process_monitor: Optional[asyncio.Task] = None

    @property
    def execution_log(self) -> list[dict[str, Any]]:
        return list(self._execution_log)

    @property
    def policy(self) -> SandboxPolicy:
        return self._policy

    async def create(self) -> str:
        self._sandbox_id = str(uuid.uuid4())
        self._work_dir = Path(tempfile.mkdtemp(prefix=f"sandbox_{self._sandbox_id}_"))
        
        # Set up disk quota if supported
        if platform.system() == "Linux":
            await self._setup_disk_quota()
        
        # Create workspace subdirectories
        (self._work_dir / "workspace").mkdir(exist_ok=True)
        (self._work_dir / "tmp").mkdir(exist_ok=True)
        
        return self._sandbox_id

    async def _setup_disk_quota(self) -> None:
        """Setup disk quota using xfs_quota or project quotas."""
        try:
            # Try to set up project quota
            proc = await asyncio.create_subprocess_exec(
                "xfs_quota", "-x", "-c", f"project -s {self._sandbox_id}",
                self._work_dir,
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL,
            )
            await proc.communicate()
            
            limit_kb = self._policy.max_disk_mb * 1024
            proc = await asyncio.create_subprocess_exec(
                "xfs_quota", "-x", "-c", f"limit -p bhard={limit_kb} {self._sandbox_id}",
                self._work_dir,
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL,
            )
            await proc.communicate()
        except FileNotFoundError:
            logger.debug("xfs_quota not available, disk quotas not enforced")

    def _validate_command(self, command: list[str]) -> str | None:
        """Validate command against policy. Returns error message or None."""
        cmd_str = " ".join(command).lower()

        # Check blocked commands
        for blocked in self._policy.blocked_commands:
            if blocked.lower() in cmd_str:
                return f"Blocked command pattern: {blocked}"

        # Check allowed commands
        if self._policy.allowed_commands:
            base_cmd = command[0] if command else ""
            if base_cmd not in self._policy.allowed_commands:
                return f"Command not in allowed list: {base_cmd}"

        # Check for path traversal
        for arg in command:
            if ".." in arg and not arg.startswith("."):
                return "Path traversal detected"

        return None

    def _build_resource_limits(self) -> dict[str, Any]:
        """Build resource limits for subprocess."""
        limits = {}
        
        if platform.system() == "Linux":
            # Memory limit (using cgroups if available)
            limits["memory"] = self._policy.max_memory_mb * 1024 * 1024
            
            # CPU limit (using nice and cpulimit)
            limits["cpu_time"] = self._policy.max_cpu_seconds
            
            # Process limit
            limits["nproc"] = self._policy.max_processes
            
            # File size limit
            limits["fsize"] = self._policy.max_file_size_mb * 1024 * 1024
        
        return limits

    async def execute(self, command: list[str], timeout: int = 30) -> SandboxResult:
        if self._work_dir is None:
            raise RuntimeError("Sandbox not created. Call create() first.")

        import time
        start_time = time.monotonic()

        error = self._validate_command(command)
        if error:
            self._log_execution(command, -1, "", error, 0)
            return SandboxResult(exit_code=-1, stdout="", stderr=error, duration_ms=0)

        actual_timeout = min(timeout, self._policy.max_cpu_seconds, self._policy.timeout_seconds)

        proc = None
        try:
            env = os.environ.copy()
            env["SANDBOX_ID"] = self._sandbox_id or ""
            env["SANDBOX_WORK_DIR"] = str(self._work_dir)
            
            # Set resource limits
            if platform.system() == "Linux":
                # Use prlimit if available
                limits = self._build_resource_limits()
                limit_args = []
                if "memory" in limits:
                    limit_args.extend(["--as", str(limits["memory"])])
                if "cpu_time" in limits:
                    limit_args.extend(["--cpu", str(limits["cpu_time"])])
                if "nproc" in limits:
                    limit_args.extend(["--nproc", str(limits["nproc"])])
                if "fsize" in limits:
                    limit_args.extend(["--fsize", str(limits["fsize"])])
                
                if limit_args:
                    command = ["prlimit"] + limit_args + command

            proc = await asyncio.create_subprocess_exec(
                *command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(self._work_dir / "workspace"),
                env=env,
            )

            try:
                stdout, stderr = await asyncio.wait_for(
                    proc.communicate(),
                    timeout=actual_timeout,
                )
            except asyncio.TimeoutError:
                if proc:
                    proc.kill()
                    await proc.wait()
                duration = (time.monotonic() - start_time) * 1000
                self._log_execution(command, -1, "", f"Timeout after {actual_timeout}s", duration)
                return SandboxResult(
                    exit_code=-1,
                    stdout="",
                    stderr=f"Timeout after {actual_timeout}s",
                    duration_ms=duration,
                )

            duration = (time.monotonic() - start_time) * 1000
            exit_code = proc.returncode or 0
            
            stdout_str = stdout.decode("utf-8", errors="replace")
            stderr_str = stderr.decode("utf-8", errors="replace")
            
            self._log_execution(command, exit_code, stdout_str, stderr_str, duration)
            
            return SandboxResult(
                exit_code=exit_code,
                stdout=stdout_str,
                stderr=stderr_str,
                duration_ms=duration,
            )
        except Exception as e:
            duration = (time.monotonic() - start_time) * 1000
            self._log_execution(command, -1, "", str(e), duration)
            return SandboxResult(
                exit_code=-1,
                stdout="",
                stderr=str(e),
                duration_ms=duration,
            )

    def _log_execution(
        self,
        command: list[str],
        exit_code: int,
        stdout: str,
        stderr: str,
        duration_ms: float,
    ) -> None:
        self._execution_log.append({
            "timestamp": time.monotonic(),
            "command": command,
            "exit_code": exit_code,
            "stdout_len": len(stdout),
            "stderr_len": len(stderr),
            "stderr_preview": stderr[:200] if stderr else "",
            "duration_ms": duration_ms,
        })
        
        # Trim log if too large
        if len(self._execution_log) > self._policy.execution_log_max_entries:
            self._execution_log = self._execution_log[-self._policy.execution_log_max_entries:]

    async def get_usage(self) -> ResourceUsage:
        """Get resource usage for the sandbox."""
        usage = ResourceUsage()
        
        if self._work_dir and self._work_dir.exists():
            try:
                # Calculate disk usage
                total_size = 0
                for root, dirs, files in os.walk(self._work_dir):
                    for file in files:
                        filepath = Path(root) / file
                        try:
                            total_size += filepath.stat().st_size
                        except OSError:
                            pass
                usage.disk_read_mb = total_size // (1024 * 1024)
            except Exception:
                pass
        
        return usage

    async def destroy(self) -> None:
        if self._work_dir and self._work_dir.exists():
            shutil.rmtree(self._work_dir, ignore_errors=True)
            self._work_dir = None
            self._sandbox_id = None
            self._execution_log.clear()


class DockerSandbox(Sandbox):
    """Enhanced Docker-based sandbox with security hardening."""

    def __init__(
        self,
        image: str = "python:3.12-slim",
        policy: SandboxPolicy | None = None,
        docker_host: str | None = None,
    ) -> None:
        self._policy = policy or SandboxPolicy()
        self._image = image
        self._docker_host = docker_host
        self._container_id: str | None = None
        self._work_dir: Path | None = None
        self._docker_available: bool | None = None
        self._seccomp_profile: Optional[str] = None

    async def _check_docker(self) -> bool:
        if self._docker_available is not None:
            return self._docker_available
        
        try:
            cmd = ["docker"]
            if self._docker_host:
                cmd.extend(["-H", self._docker_host])
            cmd.append("info")
            
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL,
            )
            await proc.communicate()
            self._docker_available = proc.returncode == 0
        except FileNotFoundError:
            self._docker_available = False
        
        return self._docker_available

    async def _create_seccomp_profile(self) -> str:
        """Create a custom seccomp profile based on policy."""
        if self._policy.seccomp_profile == "default":
            return "default"
        
        profile_name = f"superdev-{self._sandbox_id}"
        profile_path = Path(f"/etc/docker/seccomp/{profile_name}.json")
        
        # Build seccomp profile
        profile = {
            "defaultAction": "SCMP_ACT_ERRNO",
            "architectures": ["SCMP_ARCH_X86_64", "SCMP_ARCH_X86", "SCMP_ARCH_X32"],
            "syscalls": [],
        }
        
        # Allow essential syscalls
        allowed_syscalls = [
            "read", "write", "open", "close", "stat", "fstat", "lstat",
            "poll", "lseek", "mmap", "mprotect", "munmap", "brk",
            "rt_sigaction", "rt_sigprocmask", "rt_sigreturn",
            "ioctl", "pread", "pwrite", "readv", "writev",
            "access", "pipe", "select", "sched_yield",
            "mremap", "msync", "mincore", "madvise",
            "shmget", "shmat", "shmctl",
            "dup", "dup2", "pause", "nanosleep",
            "getitimer", "alarm", "setitimer",
            "getpid", "sendfile", "socket", "connect",
            "accept", "sendto", "recvfrom", "sendmsg", "recvmsg",
            "shutdown", "bind", "listen", "getsockname", "getpeername",
            "socketpair", "setsockopt", "getsockopt",
            "clone", "fork", "vfork", "execve", "exit", "wait4",
            "kill", "uname", "semget", "semop", "semctl",
            "shmdt", "msgget", "msgsnd", "msgrcv", "msgctl",
            "fcntl", "flock", "fsync", "fdatasync",
            "truncate", "ftruncate", "getdents", "getcwd",
            "chdir", "fchdir", "rename", "mkdir", "rmdir",
            "creat", "link", "unlink", "symlink", "readlink",
            "chmod", "fchmod", "chown", "fchown", "lchown",
            "umask", "gettimeofday", "getrlimit", "getrusage",
            "sysinfo", "times", "ptrace", "getuid", "syslog",
            "getgid", "setuid", "setgid", "geteuid", "getegid",
            "setpgid", "getppid", "getpgrp", "setsid", "setreuid",
            "setregid", "getgroups", "setgroups", "setresuid",
            "getresuid", "setresgid", "getresgid", "getpgid",
            "setfsuid", "setfsgid", "getsid", "capget", "capset",
            "rt_sigpending", "rt_sigtimedwait", "rt_sigqueueinfo",
            "rt_sigsuspend", "sigaltstack", "utime", "mknod",
            "uselib", "personality", "ustat", "statfs", "fstatfs",
            "sysfs", "getpriority", "setpriority", "sched_setparam",
            "sched_getparam", "sched_setscheduler", "sched_getscheduler",
            "sched_get_priority_max", "sched_get_priority_min",
            "sched_rr_get_interval", "mlock", "munlock",
            "mlockall", "munlockall", "vhangup", "modify_ldt",
            "pivot_root", "_sysctl", "prctl", "arch_prctl",
            "adjtimex", "setrlimit", "chroot", "sync",
            "acct", "settimeofday", "mount", "umount2",
            "swapon", "swapoff", "reboot", "sethostname",
            "setdomainname", "iopl", "ioperm", "create_module",
            "init_module", "delete_module", "get_kernel_syms",
            "query_module", "quotactl", "nfsservctl",
            "getpmsg", "putpmsg", "afs_syscall", "tuxcall",
            "security", "gettid", "readahead", "setxattr",
            "lsetxattr", "fsetxattr", "getxattr", "lgetxattr",
            "fgetxattr", "listxattr", "llistxattr", "flistxattr",
            "removexattr", "lremovexattr", "fremovexattr",
            "tkill", "time", "futex", "sched_setaffinity",
            "sched_getaffinity", "set_thread_area", "io_setup",
            "io_destroy", "io_getevents", "io_submit", "io_cancel",
            "get_thread_area", "lookup_dcookie", "epoll_create",
            "epoll_ctl_old", "epoll_wait_old", "remap_file_pages",
            "getdents64", "set_tid_address", "restart_syscall",
            "semtimedop", "fadvise64", "timer_create", "timer_settime",
            "timer_gettime", "timer_getoverrun", "timer_delete",
            "clock_settime", "clock_gettime", "clock_getres",
            "clock_nanosleep", "exit_group", "epoll_wait",
            "epoll_ctl", "epoll_create1", "dup3", "pipe2",
            "inotify_init1", "preadv", "pwritev", "rt_tgsigqueueinfo",
            "perf_event_open", "recvmmsg", "fanotify_init", "fanotify_mark",
            "prlimit64", "name_to_handle_at", "open_by_handle_at",
            "clock_adjtime", "syncfs", "sendmmsg", "setns",
            "getcpu", "process_vm_readv", "process_vm_writev",
            "kcmp", "finit_module", "sched_setattr", "sched_getattr",
            "renameat2", "seccomp", "getrandom", "memfd_create",
            "kexec_file_load", "bpf", "execveat", "userfaultfd",
            "membarrier", "mlock2", "copy_file_range", "preadv2",
            "pwritev2", "pkey_mprotect", "pkey_alloc", "pkey_free",
            "statx", "io_pgetevents", "rseq",
        ]
        
        for syscall in allowed_syscalls:
            profile["syscalls"].append({
                "names": [syscall],
                "action": "SCMP_ACT_ALLOW",
            })
        
        # Write profile
        try:
            profile_path.parent.mkdir(parents=True, exist_ok=True)
            profile_path.write_text(json.dumps(profile))
            self._seccomp_profile = f"localhost/{profile_name}"
        except Exception as e:
            logger.warning(f"Failed to create seccomp profile: {e}")
            self._seccomp_profile = "default"
        
        return self._seccomp_profile

    async def create(self) -> str:
        if not await self._check_docker():
            raise RuntimeError("Docker is not available. Use DefaultSandbox instead.")

        self._sandbox_id = str(uuid.uuid4())
        self._container_id = str(uuid.uuid4())[:12]
        self._work_dir = Path(tempfile.mkdtemp(prefix=f"sandbox_{self._container_id}_"))
        
        # Create seccomp profile
        await self._create_seccomp_profile()
        
        # Build docker run command
        memory_flag = f"--memory={self._policy.max_memory_mb}m"
        memory_swap_flag = f"--memory-swap={self._policy.max_memory_mb * 2}m"
        cpu_flag = f"--cpus=1.0"
        pids_limit = f"--pids-limit={self._policy.max_processes}"
        
        network_flag = "--network=none" if not self._policy.network_access else ""
        
        # Read-only root filesystem with exceptions
        readonly_flag = "--read-only"
        tmpfs_flags = [
            "--tmpfs", "/run",
            "--tmpfs", "/tmp",
            "--tmpfs", "/workspace:exec,size=" + str(self._policy.max_disk_mb) + "m",
        ]
        
        # Capability dropping
        cap_drop_flags = []
        for cap in self._policy.drop_capabilities:
            cap_drop_flags.extend(["--cap-drop", cap])
        
        # Security options
        security_opts = [
            "--security-opt", "no-new-privileges:true",
        ]
        
        if self._seccomp_profile and self._seccomp_profile != "default":
            security_opts.extend(["--security-opt", f"seccomp={self._seccomp_profile}"])
        
        # User namespace
        if self._policy.use_user_namespace:
            security_opts.extend([
                "--security-opt", f"uidmap={self._policy.uid_map}",
                "--security-opt", f"gidmap={self._policy.gid_map}",
            ])

        # Volume mounts
        volume_flags = [
            "-v", f"{self._work_dir}:/workspace",
            "-w", "/workspace",
        ]

        cmd = [
            "docker", "run", "-d",
            "--name", f"superdev-sandbox-{self._container_id}",
            memory_flag,
            memory_swap_flag,
            cpu_flag,
            pids_limit,
            *([network_flag] if network_flag else []),
            readonly_flag,
            *tmpfs_flags,
            *cap_drop_flags,
            *security_opts,
            *volume_flags,
            self._image,
            "sleep", "3600",
        ]

        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()

        if proc.returncode != 0:
            error_msg = stderr.decode() if stderr else stdout.decode()
            raise RuntimeError(f"Failed to start Docker container: {error_msg}")

        actual_id = stdout.decode().strip()
        self._container_id = actual_id[:12]
        return self._container_id

    async def execute(self, command: list[str], timeout: int = 30) -> SandboxResult:
        if self._container_id is None:
            raise RuntimeError("Sandbox not created. Call create() first.")

        import time
        start_time = time.monotonic()
        
        actual_timeout = min(timeout, self._policy.max_cpu_seconds, self._policy.timeout_seconds)
        cmd_str = " ".join(command)

        proc = None
        try:
            docker_cmd = ["docker"]
            if self._docker_host:
                docker_cmd.extend(["-H", self._docker_host])
            docker_cmd.extend(["exec", self._container_id, "sh", "-c", cmd_str])

            proc = await asyncio.create_subprocess_exec(
                *docker_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=actual_timeout)

            duration = (time.monotonic() - start_time) * 1000

            return SandboxResult(
                exit_code=proc.returncode or 0,
                stdout=stdout.decode("utf-8", errors="replace"),
                stderr=stderr.decode("utf-8", errors="replace"),
                duration_ms=duration,
            )
        except asyncio.TimeoutError:
            if proc:
                proc.kill()
                await proc.wait()
            duration = (time.monotonic() - start_time) * 1000
            return SandboxResult(
                exit_code=-1,
                stdout="",
                stderr=f"Timeout after {actual_timeout}s",
                duration_ms=duration,
            )
        except Exception as e:
            duration = (time.monotonic() - start_time) * 1000
            return SandboxResult(
                exit_code=-1,
                stdout="",
                stderr=str(e),
                duration_ms=duration,
            )

    async def get_usage(self) -> ResourceUsage:
        """Get resource usage from Docker stats."""
        usage = ResourceUsage()
        
        if self._container_id:
            try:
                proc = await asyncio.create_subprocess_exec(
                    "docker", "stats", "--no-stream", "--format",
                    "{{.CPUPerc}},{{.MemUsage}},{{.NetIO}},{{.BlockIO}}",
                    self._container_id,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
                stdout, _ = await proc.communicate()
                
                if stdout:
                    line = stdout.decode().strip()
                    if line:
                        cpu_str, mem_str, net_str, block_str = line.split(",")
                        
                        # Parse CPU percentage
                        cpu_pct = float(cpu_str.replace("%", ""))
                        usage.cpu_time_ms = int(cpu_pct * 100)
                        
                        # Parse memory
                        if "MiB" in mem_str:
                            mem_used = float(mem_str.split("/")[0].replace("MiB", "").strip())
                            usage.memory_peak_mb = int(mem_used)
                        
                        # Parse network I/O
                        if "B" in net_str:
                            parts = net_str.split("/")
                            if len(parts) == 2:
                                rx_str = parts[0].strip()
                                tx_str = parts[1].strip()
                                usage.network_rx_bytes = self._parse_bytes(rx_str)
                                usage.network_tx_bytes = self._parse_bytes(tx_str)
                        
                        # Parse block I/O
                        if "B" in block_str:
                            parts = block_str.split("/")
                            if len(parts) == 2:
                                read_str = parts[0].strip()
                                write_str = parts[1].strip()
                                usage.disk_read_mb = self._parse_bytes(read_str) // (1024 * 1024)
                                usage.disk_write_mb = self._parse_bytes(write_str) // (1024 * 1024)
            except Exception:
                pass
        
        return usage

    def _parse_bytes(self, s: str) -> int:
        s = s.strip().upper()
        multipliers = {"K": 1024, "M": 1024**2, "G": 1024**3, "T": 1024**4}
        for suffix, mult in multipliers.items():
            if s.endswith(suffix):
                return int(float(s[:-len(suffix)]) * mult)
        return int(float(s))

    async def destroy(self) -> None:
        if self._container_id:
            try:
                cmd = ["docker"]
                if self._docker_host:
                    cmd.extend(["-H", self._docker_host])
                cmd.extend(["rm", "-f", self._container_id])
                
                proc = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.DEVNULL,
                    stderr=asyncio.subprocess.DEVNULL,
                )
                await proc.communicate()
            except Exception:
                pass
            self._container_id = None

        if self._work_dir and self._work_dir.exists():
            shutil.rmtree(self._work_dir, ignore_errors=True)
            self._work_dir = None


class SandboxPool:
    """Pool of pre-warmed sandboxes for faster execution."""
    
    def __init__(
        self,
        size: int = 5,
        sandbox_type: str = "default",
        policy: SandboxPolicy | None = None,
        **sandbox_kwargs,
    ):
        self._size = size
        self._sandbox_type = sandbox_type
        self._policy = policy
        self._sandbox_kwargs = sandbox_kwargs
        self._available: asyncio.Queue[Sandbox] = asyncio.Queue()
        self._in_use: set[Sandbox] = set()
        self._created = 0

    async def acquire(self) -> Sandbox:
        if self._available.empty() and self._created < self._size:
            sandbox = await self._create_sandbox()
            self._created += 1
            self._in_use.add(sandbox)
            return sandbox
        
        sandbox = await self._available.get()
        self._in_use.add(sandbox)
        return sandbox

    async def release(self, sandbox: Sandbox) -> None:
        if sandbox in self._in_use:
            self._in_use.remove(sandbox)
            await self._available.put(sandbox)

    async def _create_sandbox(self) -> Sandbox:
        if self._sandbox_type == "docker":
            sandbox = DockerSandbox(policy=self._policy, **self._sandbox_kwargs)
        else:
            sandbox = DefaultSandbox(policy=self._policy)
        
        await sandbox.create()
        return sandbox

    async def close(self) -> None:
        while not self._available.empty():
            sandbox = self._available.get_nowait()
            await sandbox.destroy()
        
        for sandbox in self._in_use:
            await sandbox.destroy()
        
        self._in_use.clear()


def create_sandbox(
    use_docker: bool = False,
    policy: SandboxPolicy | None = None,
    **kwargs: Any,
) -> Sandbox:
    """Factory function to create the appropriate sandbox."""
    if use_docker:
        try:
            return DockerSandbox(policy=policy, **kwargs)
        except Exception:
            logger.warning("Docker sandbox creation failed, falling back to default")
    return DefaultSandbox(policy=policy)