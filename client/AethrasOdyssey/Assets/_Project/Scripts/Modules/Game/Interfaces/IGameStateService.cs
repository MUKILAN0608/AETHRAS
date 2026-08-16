namespace Aethras.Modules.Game.Interfaces
{
    /// <summary>Top-level game state machine: Bootstrap → MainMenu → Loading → Exploration → Dialogue → Puzzle → Paused.</summary>
    public interface IGameStateService
    {
        string CurrentStateName { get; }
        bool TryEnterState(string stateName);
        void RegisterStateTransitionHandler(System.Action<string, string> handler);
    }
}
