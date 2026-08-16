using System;

namespace Aethras.Core.Events
{
    /// <summary>
    /// Central publish/subscribe bus for decoupled inter-module communication.
    /// Modules MUST NOT reference each other directly; they communicate via events.
    /// </summary>
    public interface IEventBus
    {
        void Subscribe<TEvent>(Action<TEvent> handler) where TEvent : struct;
        void Unsubscribe<TEvent>(Action<TEvent> handler) where TEvent : struct;
        void Publish<TEvent>(TEvent gameEvent) where TEvent : struct;
        void ClearAllSubscriptions();
    }
}
