"""AI Physics Engine — scene physics simulation (blueprint Volume 3).

Gravity, particles, cloth, fluid, smoke, fire, wind, collisions, rigid and
soft bodies, destruction, weather and environment physics.
"""
from modules.ai_video_studio.ai_physics.physics_engine import PhysicsEngine, get_physics_engine
from modules.ai_video_studio.ai_physics.gravity import Gravity
from modules.ai_video_studio.ai_physics.particles import Particles
from modules.ai_video_studio.ai_physics.cloth_simulation import ClothSimulation
from modules.ai_video_studio.ai_physics.fluid_simulation import FluidSimulation
from modules.ai_video_studio.ai_physics.smoke_simulation import SmokeSimulation
from modules.ai_video_studio.ai_physics.fire_simulation import FireSimulation
from modules.ai_video_studio.ai_physics.wind_engine import WindEngine
from modules.ai_video_studio.ai_physics.collision_engine import CollisionEngine
from modules.ai_video_studio.ai_physics.rigid_body import RigidBody
from modules.ai_video_studio.ai_physics.soft_body import SoftBody
from modules.ai_video_studio.ai_physics.destruction_engine import DestructionEngine
from modules.ai_video_studio.ai_physics.weather_engine import WeatherEngine
from modules.ai_video_studio.ai_physics.environment_physics import EnvironmentPhysics

__all__ = [
    "PhysicsEngine",
    "get_physics_engine",
    "Gravity",
    "Particles",
    "ClothSimulation",
    "FluidSimulation",
    "SmokeSimulation",
    "FireSimulation",
    "WindEngine",
    "CollisionEngine",
    "RigidBody",
    "SoftBody",
    "DestructionEngine",
    "WeatherEngine",
    "EnvironmentPhysics",
]
