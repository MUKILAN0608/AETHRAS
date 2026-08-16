namespace Aethras.Core.Commands
{
    /// <summary>
    /// Marker interface for command pattern implementations.
    /// Commands represent intent; handlers execute side effects.
    /// </summary>
    public interface ICommand { }

    /// <summary>
    /// Executes a command and returns whether it succeeded.
    /// </summary>
    public interface ICommandHandler<in TCommand> where TCommand : ICommand
    {
        bool Handle(TCommand command);
    }
}
