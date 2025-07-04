from langchain_text_splitters import CharacterTextSplitter, RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from langflow.custom import Component
from langflow.io import DropdownInput, HandleInput, IntInput, MessageTextInput, Output, BoolInput
from langflow.schema import Data, DataFrame
from langflow.utils.util import unescape_string
import re


class OptimizedSplitTextComponent(Component):
    display_name: str = "Obra Price Splitter"
    description: str = "Split text from price files (CPOS, SICRO, SINAPI) optimized for RAG queries."
    icon = "scissors-line-dashed"
    name = "ObraPriceSplitter"

    inputs = [
        HandleInput(
            name="data_inputs",
            display_name="Price Data or DataFrame",
            info="The price data with texts to split in chunks optimized for construction services.",
            input_types=["Data", "DataFrame"],
            required=True,
        ),
        IntInput(
            name="chunk_size",
            display_name="Chunk Size",
            info=(
                "Maximum length of each chunk. Optimized for price data: "
                "1000-2000 for detailed descriptions, 500-1000 for quick queries."
            ),
            value=1500,  # ✅ Otimizado para descrições de serviços
        ),
        IntInput(
            name="chunk_overlap",
            display_name="Chunk Overlap",
            info="Number of characters to overlap between chunks. Higher overlap improves context retention.",
            value=300,  # ✅ Aumentado para manter contexto entre chunks
        ),
        MessageTextInput(
            name="separator",
            display_name="Separator",
            info=(
                "Character to split on. For price files: \\n for lines, \\n\\n for sections. "
                "Recommended: \\n for line-by-line splitting."
            ),
            value="\n",
        ),
        MessageTextInput(
            name="text_key",
            display_name="Text Key",
            info="The key to use for the text column in the data.",
            value="text",
            advanced=True,
        ),
        DropdownInput(
            name="splitter_type",
            display_name="Splitter Type",
            info="Type of text splitter to use. Recursive is better for varied content.",
            options=["Character", "Recursive"],
            value="Recursive",  # ✅ Melhor para dados variados
            advanced=True,
        ),
        BoolInput(
            name="preserve_headers",
            display_name="Preserve Headers",
            info="Keep header information in each chunk for better context.",
            value=True,  # ✅ Importante para manter estrutura
            advanced=True,
        ),
        BoolInput(
            name="smart_splitting",
            display_name="Smart Splitting",
            info="Use intelligent splitting that respects service boundaries.",
            value=True,  # ✅ Evita cortar no meio de serviços
            advanced=True,
        ),
        DropdownInput(
            name="keep_separator",
            display_name="Keep Separator",
            info="Whether to keep the separator in the output chunks and where to place it.",
            options=["False", "True", "Start", "End"],
            value="True",  # ✅ Mantém separadores para contexto
            advanced=True,
        ),
    ]

    outputs = [
        Output(display_name="Price Chunks", name="chunks", method="split_text"),
        Output(display_name="Price DataFrame", name="dataframe", method="as_dataframe"),
    ]

    def _docs_to_data(self, docs) -> list[Data]:
        """Convert documents to Data objects with proper metadata."""
        data_list = []
        for doc in docs:
            # Create Data object with correct parameters - data should be a dict
            data_obj = Data(
                data={"text": doc.page_content}
            )
            data_list.append(data_obj)
        return data_list

    def _fix_separator(self, separator: str) -> str:
        """Fix common separator issues and convert to proper format."""
        if separator == "/n":
            return "\n"
        if separator == "/t":
            return "\t"
        return separator

    def _smart_split_price_data(self, text: str) -> list[str]:
        """Intelligent splitting that respects service boundaries."""
        lines = text.split('\n')
        chunks = []
        current_chunk = []
        current_size = 0
        
        for line in lines:
            # Check if line is a service entry (starts with code pattern)
            if re.match(r'^\d{7}\s+', line):  # Service code pattern
                # If current chunk is getting large, start new chunk
                if current_size > self.chunk_size and current_chunk:
                    chunks.append('\n'.join(current_chunk))
                    current_chunk = []
                    current_size = 0
                
                # Add header to new chunk if enabled
                if self.preserve_headers and chunks:
                    header_lines = [l for l in lines[:5] if 'CODIGO' in l or 'DESCRICAO' in l]
                    if header_lines:
                        current_chunk.extend(header_lines)
                        current_size += sum(len(l) for l in header_lines)
            
            current_chunk.append(line)
            current_size += len(line) + 1  # +1 for newline
        
        # Add remaining chunk
        if current_chunk:
            chunks.append('\n'.join(current_chunk))
        
        return chunks

    def split_text_base(self):
        separator = self._fix_separator(self.separator)
        separator = unescape_string(separator)

        if isinstance(self.data_inputs, DataFrame):
            if not len(self.data_inputs):
                msg = "DataFrame is empty"
                raise TypeError(msg)

            self.data_inputs.text_key = self.text_key
            try:
                documents = self.data_inputs.to_lc_documents()
            except Exception as e:
                msg = f"Error converting DataFrame to documents: {e}"
                raise TypeError(msg) from e
        else:
            if not self.data_inputs:
                msg = "No data inputs provided"
                raise TypeError(msg)

            documents = []
            if isinstance(self.data_inputs, Data):
                self.data_inputs.text_key = self.text_key
                documents = [self.data_inputs.to_lc_document()]
            else:
                try:
                    documents = [input_.to_lc_document() for input_ in self.data_inputs if isinstance(input_, Data)]
                    if not documents:
                        msg = f"No valid Data inputs found in {type(self.data_inputs)}"
                        raise TypeError(msg)
                except AttributeError as e:
                    msg = f"Invalid input type in collection: {e}"
                    raise TypeError(msg) from e

        try:
            # Convert string 'False'/'True' to boolean
            keep_sep = self.keep_separator
            if isinstance(keep_sep, str):
                if keep_sep.lower() == "false":
                    keep_sep = False
                elif keep_sep.lower() == "true":
                    keep_sep = True
                elif keep_sep.lower() == "start":
                    keep_sep = "start"
                elif keep_sep.lower() == "end":
                    keep_sep = "end"
                else:
                    keep_sep = False

            # Choose splitter type
            if self.splitter_type == "Recursive":
                splitter = RecursiveCharacterTextSplitter(
                    chunk_overlap=self.chunk_overlap,
                    chunk_size=self.chunk_size,
                    separators=["\n\n", "\n", ".", " ", ""],  # ✅ Otimizado para dados de preços
                    keep_separator=keep_sep,
                )
            else:
                splitter = CharacterTextSplitter(
                    chunk_overlap=self.chunk_overlap,
                    chunk_size=self.chunk_size,
                    separator=separator,
                    keep_separator=keep_sep,
                )

            # Apply smart splitting if enabled
            if self.smart_splitting:
                # Process each document with smart splitting
                smart_docs = []
                for doc in documents:
                    if hasattr(doc, 'page_content'):
                        smart_chunks = self._smart_split_price_data(doc.page_content)
                        for chunk in smart_chunks:
                            # Create new document for each smart chunk
                            new_doc = Document(
                                page_content=chunk,
                                metadata=doc.metadata if hasattr(doc, 'metadata') else {}
                            )
                            smart_docs.append(new_doc)
                documents = smart_docs

            # Split documents
            split_docs = splitter.split_documents(documents)
            
            # Log statistics
            self.log(f"📊 Split {len(documents)} documents into {len(split_docs)} chunks")
            self.log(f"⚙️ Chunk size: {self.chunk_size}, Overlap: {self.chunk_overlap}")
            self.log(f"🧠 Smart splitting: {self.smart_splitting}, Preserve headers: {self.preserve_headers}")
            
            return split_docs
            
        except Exception as e:
            msg = f"Error splitting text: {e}"
            raise TypeError(msg) from e

    def split_text(self) -> list[Data]:
        """Split text and return as Data objects."""
        return self._docs_to_data(self.split_text_base())

    def as_dataframe(self) -> DataFrame:
        """Return split text as DataFrame."""
        return DataFrame(self.split_text())
