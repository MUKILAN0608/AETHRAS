namespace Aethras.Core.StateMachine
{
    /// <summary>
    /// Generic finite state machine for game flow, dialogue, puzzles, and UI states.
    /// </summary>
    public interface IStateMachine<TState> where TState : struct, System.Enum
    {
        TState CurrentState { get; }
        bool CanTransitionTo(TState targetState);
        bool TryTransitionTo(TState targetState);
        void ForceTransitionTo(TState targetState);
    }
}
