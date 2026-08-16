using System.Threading;
using System.Threading.Tasks;

namespace Aethras.Modules.Scene.Interfaces
{
    /// <summary>Handles additive/async scene loading via Addressables.</summary>
    public interface ISceneLoader
    {
        Task LoadSceneAsync(string sceneAddress, CancellationToken cancellationToken = default);
        Task UnloadSceneAsync(string sceneAddress, CancellationToken cancellationToken = default);
        Task LoadAdditiveAsync(string sceneAddress, CancellationToken cancellationToken = default);
        float LoadingProgress { get; }
    }
}
