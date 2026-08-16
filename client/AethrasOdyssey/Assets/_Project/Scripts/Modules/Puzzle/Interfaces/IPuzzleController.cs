namespace Aethras.Modules.Puzzle.Interfaces
{
    /// <summary>Puzzle lifecycle coordinator using Strategy pattern for puzzle types.</summary>
    public interface IPuzzleController
    {
        bool IsPuzzleActive { get; }
        void StartPuzzle(string puzzleId);
        void SubmitSolution(string puzzleId, string solutionPayload);
        void AbortPuzzle();
    }

    /// <summary>Strategy interface for individual puzzle type implementations.</summary>
    public interface IPuzzleStrategy
    {
        string PuzzleTypeId { get; }
        bool ValidateSolution(string solutionPayload);
        void OnPuzzleStarted(string puzzleId);
        void OnPuzzleCompleted(string puzzleId);
    }
}
