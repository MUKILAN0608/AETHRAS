namespace Aethras.AI.Client.DTOs
{
    /// <summary>Generic wrapper for REST API responses from FastAPI backend.</summary>
    public sealed class ApiResponseDto<T>
    {
        public bool IsSuccess { get; set; }
        public int StatusCode { get; set; }
        public T Data { get; set; }
        public string ErrorMessage { get; set; }
    }
}
