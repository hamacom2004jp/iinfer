from pathlib import Path
from PIL import Image
from iinfer.app import common, predict
from iinfer.app.commons import convert
from typing import List, Tuple, Union
import logging


SITE = 'https://huggingface.co/mmnga/ELYZA-japanese-Llama-2-7b-fast-instruct-gguf/tree/main'
IMAGE_WIDTH = 640
IMAGE_HEIGHT = 640
REQUIREd_MODEL_CONF = False
REQUIREd_MODEL_WEIGHT = False

class LlamaIndex_ELYZA_Search(predict.TorchPredict):
    def __init__(self, logger:logging.Logger) -> None:
        super().__init__(logger)

    def post_deploy(self, deploy_dir:Path, conf:dict) -> None:
        """
        デプロイ後の処理を行う関数です。
        deployコマンド実行時に呼び出されます。
        この関数内でデプロイ後の処理を実装してください。
        
        Args:
            deploy_dir (Path): デプロイディレクトリのパス
            conf (dict): デプロイ設定
        """
        pass

    def create_session(self, deploy_dir:Path, model_path:Path, model_conf_path:Path, model_provider:str, gpu_id:int=None):
        """
        推論セッションを作成する関数です。
        startコマンド実行時に呼び出されます。
        この関数内でAIモデルのロードを行い、推論準備を完了するようにしてください。
        戻り値の推論セッションの型は問いません。

        Args:
            deploy_dir (Path): デプロイディレクトリのパス
            model_path (Path): モデルファイルのパス
            model_conf_path (Path): モデル設定ファイルのパス
            gpu_id (int, optional): GPU ID. Defaults to None.

        Returns:
            推論セッション
        """
        conf = common.loadopt(deploy_dir / 'conf.json')
        opt = common.loadopt(conf['model_conf_file']) if conf['model_conf_file'] is not None else dict()
        self.temperature = common.getopt(opt, 'temperature', preval=0, withset=False)
        self.n_ctx = common.getopt(opt, 'n_ctx', preval=4096, withset=False)
        self.n_gpu_layers = common.getopt(opt, 'n_gpu_layers', preval=1, withset=False)
        # elyza/ELYZA-japanese-Llama-2-7b-fast-instruct
        model_name = common.getopt(opt, 'model_name', preval=model_path, withset=False)
        embedd_model_name = common.getopt(opt, 'embedd_model_name', preval='intfloat/multilingual-e5-base', withset=False)
        doc_path = Path(common.getopt(opt, 'doc_path', preval=deploy_dir/'docs', withset=False))
        if not doc_path.exists():
            doc_path.mkdir(parents=True, exist_ok=True)

        from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
        from llama_index.core.ingestion import IngestionPipeline
        from llama_index.core.node_parser import SentenceSplitter
        from llama_index.embeddings.huggingface import HuggingFaceEmbedding
        from llama_index.llms.huggingface import HuggingFaceLLM
        from transformers import BitsAndBytesConfig
        import torch

        documents = SimpleDirectoryReader(input_dir=doc_path, exclude_hidden=False).load_data()
        Settings.text_splitter = SentenceSplitter(chunk_size=1024)
        Settings.transformations = [Settings.text_splitter]
        Settings.embed_model = HuggingFaceEmbedding(model_name=embedd_model_name, cache_folder=deploy_dir)
        quantization_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_use_double_quant=True,
        )
        Settings.llm = HuggingFaceLLM(model_name=model_name, tokenizer_name=model_name,
                                      context_window=512, # maximum input size to the LLM
                                      max_new_tokens=256, # number of tokens reserved for text generation.
                                      model_kwargs=dict(cache_dir=deploy_dir),
                                      generate_kwargs=dict(temperature=0.7, top_k=50, top_p=0.95))
        index = VectorStoreIndex.from_documents(documents, show_progress=True, embed_model=Settings.embed_model)
        """
        import llama_index
        import langchain
        llm = langchain.llms.LlamaCpp(model_path=conf['model_file'], temperature=self.temperature, n_ctx=self.n_ctx, n_gpu_layers=self.n_gpu_layers)
        llm_predictor = llama_index.llm_predictor.LLMPredictor(llm=llm)
        embed_model = llama_index.embeddings.LangchainEmbedding(
                        langchain.embeddings.huggingface.HuggingFaceEmbeddings(model_name=self.model_name))
        service_context = llama_index.ServiceContext.from_defaults(llm_predictor=llm_predictor, embed_model=embed_model)
        # ドキュメントのインデックス化
        documents = llama_index.SimpleDirectoryReader('./inputs').load_data()
        model = llama_index.GPTVectorStoreIndex.from_documents(documents, service_context=service_context)
        """

        return index

    def predict(self, model, img_width:int, img_height:int, input_data:Union[Image.Image, str], labels:List[str]=None, colors:List[Tuple[int]]=None, nodraw:bool=False):
        """
        予測を行う関数です。
        predictコマンドやcaptureコマンド実行時に呼び出されます。
        引数のinput_dataが画像の場合RGBですので、戻り値の出力画像もRGBにしてください。
        戻り値の推論結果のdictは、通常推論結果項目ごとに値(list)を設定します。

        Args:
            model: 推論セッション
            img_width (int): モデルのINPUTサイズ（input_dataが画像の場合は、画像の幅）
            img_height (int): モデルのINPUTサイズ（input_dataが画像の場合は、画像の高さ）
            input_data (Image | str): 推論するデータ（画像の場合RGB配列であること）
            labels (List[str], optional): クラスラベルのリスト. Defaults to None.
            colors (List[Tuple[int]], optional): ボックスの色のリスト. Defaults to None.
            nodraw (bool, optional): 描画フラグ. Defaults to False.

        Returns:
            Tuple[Dict[str, Any], Image]: 予測結果と出力画像(RGB)のタプル
        """
        template = """
            <s>[INST] <<SYS>> こんにちは、私はELYZAです。私は日本語の質問に答えることができます。
            あなたは誠実で優秀な日本人のアシスタントです。
            以下の「コンテキスト情報」と「制約条件」を元に質問に回答してください。

            # コンテキスト情報

            ---------------------
            {context_str}
            ---------------------

            # 制約条件

            - コンテキスト情報はマークダウン形式で書かれています。
            - 「コンテキスト情報に」のような書き方を絶対に回答に含めないでください。
            - コンテキスト情報に無い情報は絶対に回答に含めないでください。
            - コンテキスト情報の内容を丸投げするのではなく、絶対にきちんとした文章にして回答してください。
            - 質問の答えを知らない場合は、誤った情報を共有しないでください。
            <</SYS>>

            {query_str} [/INST]
            """

        from llama_index.core import VectorStoreIndex, Settings
        index:VectorStoreIndex = model
        query_engine = index.as_query_engine()#text_qa_template=llama_index.prompts.prompts.QuestionAnswerPrompt(template))
        res_msg = query_engine.query(input_data)

        return dict(prompt=input_data, responce=str(res_msg).strip()), None
