namespace Aethras.Modules.Memory.Interfaces
{
    /// <summary>Local cache of player memory graph; syncs with backend Memory Graph.</summary>
    public interface IMemoryService
    {
        void StoreMemory(string memoryTag, string value);
        bool TryGetMemory(string memoryTag, out string value);
        void InvalidateMemory(string memoryTag);
        string[] GetActiveMemoryTags();
    }
}
