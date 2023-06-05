import hashlib

def generate_id(chat_id):
    # gera o sessionId (lex) baseado no chatId (telegram)
    print(hashlib.sha256(chat_id.encode('utf-8')).hexdigest())
    return hashlib.sha256(chat_id.encode('utf-8')).hexdigest()[:8]