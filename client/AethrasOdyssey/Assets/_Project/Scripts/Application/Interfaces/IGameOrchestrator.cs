using System.Threading;
using System.Threading.Tasks;

namespace Aethras.Application.Interfaces
{
    /// <summary>
    /// Application-layer orchestrator for high-level game lifecycle.
    /// Coordinates modules without owning their internal logic.
    /// </summary>
    public interface IGameOrchestrator
    {
        Task InitializeAsync(CancellationToken cancellationToken = default);
        Task StartNewGameAsync(CancellationToken cancellationToken = default);
        Task LoadGameAsync(string saveSlotId, CancellationToken cancellationToken = default);
        Task PauseAsync(CancellationToken cancellationToken = default);
        Task ResumeAsync(CancellationToken cancellationToken = default);
        Task ShutdownAsync(CancellationToken cancellationToken = default);
    }
}
