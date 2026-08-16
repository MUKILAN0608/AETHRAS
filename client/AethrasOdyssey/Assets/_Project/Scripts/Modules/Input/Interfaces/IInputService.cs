namespace Aethras.Modules.Input.Interfaces
{
    /// <summary>Abstracts Unity Input System; publishes input events to the Event Bus.</summary>
    public interface IInputService
    {
        bool IsInputEnabled { get; }
        void EnableInput();
        void DisableInput();
        void RebindAction(string actionId);
    }
}
