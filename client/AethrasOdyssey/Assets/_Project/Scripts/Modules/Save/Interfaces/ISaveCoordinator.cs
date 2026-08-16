namespace Aethras.Modules.Save.Interfaces
{
    /// <summary>Module-level save coordinator; delegates persistence to Application ISaveLoadService.</summary>
    public interface ISaveCoordinator
    {
        void RequestAutoSave();
        void RequestManualSave(string slotId);
        bool CanSave { get; }
    }
}
