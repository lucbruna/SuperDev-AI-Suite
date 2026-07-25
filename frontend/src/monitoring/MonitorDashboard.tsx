export function MonitorDashboard() {
  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">Monitoring Dashboard</h1>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white p-4 rounded-lg shadow">
          <h3 className="text-gray-500 text-sm">CPU Usage</h3>
          <p className="text-2xl font-bold">45%</p>
        </div>
        <div className="bg-white p-4 rounded-lg shadow">
          <h3 className="text-gray-500 text-sm">Memory</h3>
          <p className="text-2xl font-bold">2.1 GB</p>
        </div>
        <div className="bg-white p-4 rounded-lg shadow">
          <h3 className="text-gray-500 text-sm">Requests/min</h3>
          <p className="text-2xl font-bold">1,234</p>
        </div>
      </div>
    </div>
  );
}
