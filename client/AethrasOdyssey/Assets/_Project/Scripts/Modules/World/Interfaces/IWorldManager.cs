namespace Aethras.Modules.World.Interfaces
{
    /// <summary>Orchestrates interconnected world instances, lore triggers, and dynamic events.</summary>
    public interface IWorldManager
    {
        string CurrentWorldId { get; }
        bool IsWorldLoaded { get; }
        void LoadWorld(string worldId);
        void UnloadCurrentWorld();
        void RegisterDynamicEvent(string eventId);
    }
}
