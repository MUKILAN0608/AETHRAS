namespace Aethras.Modules.Narrative.Interfaces
{
    /// <summary>Client-side narrative state machine; syncs with backend Narrative Engine.</summary>
    public interface INarrativeStateService
    {
        string CurrentStoryBeatId { get; }
        void SetStoryBeat(string beatId);
        void RegisterLoreDiscovery(string loreId);
        bool HasDiscoveredLore(string loreId);
    }
}
