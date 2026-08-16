namespace Aethras.Modules.NPC.Interfaces
{
    /// <summary>Spawns, registers, and tracks NPC runtime state per world.</summary>
    public interface INpcManager
    {
        void RegisterNpc(string npcId, UnityEngine.GameObject instance);
        void UnregisterNpc(string npcId);
        bool TryGetNpc(string npcId, out UnityEngine.GameObject instance);
        void SetNpcAvailability(string npcId, bool isAvailable);
    }
}
