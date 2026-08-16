using System;

namespace Aethras.Core.DependencyInjection
{
    /// <summary>
    /// Composition root contract. Bootstrap registers all services here.
    /// Prefer constructor injection; use Resolve only at composition boundaries.
    /// </summary>
    public interface IDependencyContainer
    {
        void RegisterSingleton<TInterface, TImplementation>() where TImplementation : class, TInterface;
        void RegisterTransient<TInterface, TImplementation>() where TImplementation : class, TInterface;
        void RegisterInstance<TInterface>(TInterface instance) where TInterface : class;
        TInterface Resolve<TInterface>() where TInterface : class;
        object Resolve(Type serviceType);
    }
}
