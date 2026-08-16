namespace Aethras.Modules.Player.Interfaces
{
    /// <summary>Manages player locomotion, interaction radius, and exploration state.</summary>
    public interface IPlayerController
    {
        bool IsMoving { get; }
        bool CanInteract { get; }
        void SetMovementEnabled(bool enabled);
        void SetInteractionEnabled(bool enabled);
    }
}
