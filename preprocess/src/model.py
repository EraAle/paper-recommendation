from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

# 사용할 수 있는 모델들 매핑
llm_name_dict = {
    "Mistral-7B-Instruct-v0.2": "mistralai/Mistral-7B-Instruct-v0.2",
    "Qwen2.5-7B-Instruct": "Qwen/Qwen2.5-7B-Instruct",
    "Llama-3.1-8B-Instruct": "meta-llama/Meta-Llama-3.1-8B-Instruct",
    "Llama-2-7B-Chat": "meta-llama/Llama-2-7b-chat-hf"
}


def get_model_and_tokenizer(model_name: str, use_cuda: bool = True, prefer_8bit: bool = True):
    if model_name not in llm_name_dict:
        model_id = "mistralai/Mistral-7B-Instruct-v0.2"
    else:
        model_id = llm_name_dict[model_name]

    print(f"Loading model: {model_name} ({model_id})")
    tokenizer = AutoTokenizer.from_pretrained(model_id)

    kwargs = {}
    if use_cuda:
        kwargs["device_map"] = "auto"

    if "8B" in model_name or "8b" in model_name or not prefer_8bit:
        print(">>> Using 4-bit NF4 quantization (safe mode)")
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype="float16"
        )
    else:
        print(">>> Using 8-bit quantization (max VRAM usage, better accuracy)")
        bnb_config = BitsAndBytesConfig(
            load_in_8bit=True
        )

    kwargs["quantization_config"] = bnb_config

    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        **kwargs
    )

    return model, tokenizer

# 사용 예시
if __name__ == "__main__":
    model, tokenizer = get_model_and_tokenizer("Mistral-7B-Instruct-v0.2", prefer_8bit=False)
    inputs = tokenizer("recommend me dinner menu", return_tensors="pt").to(model.device)
    outputs = model.generate(**inputs, max_new_tokens=1000)
    print(tokenizer.decode(outputs[0], skip_special_tokens=True))