using System.Threading;
using System.Threading.Tasks;

namespace Aethras.Modules.Loading.Interfaces
{
    /// <summary>Unified loading pipeline for worlds, scenes, and AI warm-up.</summary>
    public interface ILoadingPipeline
    {
        Task ExecuteLoadSequenceAsync(string loadContextId, CancellationToken cancellationToken = default);
        float Progress { get; }
        string CurrentStepLabel { get; }
        bool IsLoading { get; }
    }
}
