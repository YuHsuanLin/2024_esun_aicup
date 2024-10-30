# from typing import List, Callable, Optional, Tuple

# class SlidingWindowSplitter:
#     def __init__(
#         self,
#         chunk_size: int,
#         chunk_overlap: int,
#         tokenizer: Optional[Callable[[str], List[str]]] = None,
#         separator: str = "",
#     ):
#         if chunk_overlap >= chunk_size:
#             raise ValueError("chunk_overlap must be smaller than chunk_size")
#         self.chunk_size = chunk_size
#         self.chunk_overlap = chunk_overlap
#         self.separator = separator
#         self._tokenizer = tokenizer or self.default_tokenizer

#     def default_tokenizer(self, text: str) -> List[str]:
#         """Default tokenizer that splits text into words."""
#         return text.split(self.separator) if self.separator else text.split()

#     def split(self, text: str) -> List[str]:
#         """Split text into chunks based on token size."""
#         if not text:
#             return []
            
#         # 如果是中文文本，直接按字符處理
#         if not self.separator:
#             chunks = []
#             start = 0
#             while start < len(text):
#                 # 取出當前chunk
#                 end = start + self.chunk_size
#                 current_chunk = text[start:end]
#                 chunks.append(current_chunk)
                
#                 # 下一個chunk的起始位置需要扣除重疊部分
#                 start = end - self.chunk_overlap
                
#             return self._postprocess_chunks(chunks)
        
#         # 如果有分隔符，使用原來的分詞邏輯
#         words = self._tokenizer(text)
#         chunks = []
#         current_chunk = []
#         current_length = 0
        
#         for word in words:
#             word_length = len(word)
#             separator_length = len(self.separator) if current_chunk else 0
#             total_length = current_length + word_length + separator_length
            
#             if total_length > self.chunk_size and current_chunk:
#                 chunks.append(self.separator.join(current_chunk))
#                 if self.chunk_overlap > 0:
#                     overlap_size = min(self.chunk_overlap, len(current_chunk))
#                     current_chunk = current_chunk[-overlap_size:]
#                     current_length = len(self.separator.join(current_chunk))
#                 else:
#                     current_chunk = []
#                     current_length = 0
            
#             current_chunk.append(word)
#             current_length = len(self.separator.join(current_chunk))
        
#         if current_chunk:
#             chunks.append(self.separator.join(current_chunk))
            
#         return self._postprocess_chunks(chunks)

#     def _postprocess_chunks(self, chunks: List[str]) -> List[str]:
#         """Post-process chunks to remove whitespace only chunks and trim."""
#         new_chunks = []
#         for chunk in chunks:
#             stripped_chunk = chunk.strip()
#             if stripped_chunk:
#                 new_chunks.append(stripped_chunk)
#         return new_chunks

#     def _token_size(self, text: str) -> int:
#         return len(self._tokenizer(text))

# # # Example usage
# # splitter = SlidingWindowSplitter(chunk_size=100, chunk_overlap=20)
# # text = "這是一段需要分塊的文本。它包含多個句子和段落。"
# # chunks = splitter.split(text)
# # for i, chunk in enumerate(chunks):
# #     print(f"Chunk {i+1}: {chunk}")