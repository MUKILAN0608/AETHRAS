namespace Aethras.Modules.Camera.Interfaces
{
    /// <summary>Cinematic and exploration camera control without gameplay coupling.</summary>
    public interface ICameraDirector
    {
        void SetFollowTarget(UnityEngine.Transform target);
        void BlendToPreset(string presetId, float duration);
        void SetExplorationMode();
        void SetDialogueMode();
        void SetPuzzleMode();
    }
}
