namespace Aethras.Domain.Interfaces
{
    /// <summary>
    /// Generic repository for domain aggregate persistence.
    /// Implementations live in Infrastructure; modules consume via Application layer.
    /// </summary>
    public interface IRepository<TEntity, TKey> where TEntity : class
    {
        TEntity GetById(TKey id);
        bool TryGetById(TKey id, out TEntity entity);
        void Save(TEntity entity);
        void Delete(TKey id);
        bool Exists(TKey id);
    }
}
