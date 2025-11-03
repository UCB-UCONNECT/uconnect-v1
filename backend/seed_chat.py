# ---------------- SCRIPT PARA POPULAR DADOS DE TESTE DO CHAT ---------------- #
"""
Execute este script uma vez para criar conversas e mensagens de teste.
Uso: python seed_chat.py
"""
from datetime import datetime, timedelta
from sqlalchemy import or_
from sqlalchemy.orm import Session
from app.db import SessionLocal
from app import models
from app.utils import get_password_hash

def create_test_data():
    db = SessionLocal()
    
    try:
        print("🔄 Criando utilizadores de teste...")
        
        users_data = [
            {
                "registration": "2024001",
                "name": "Gabriel Aluno",
                "email": "gabriel@example.com",
                "role": models.UserRole.student,
                "password": "senha123"
            },
            {
                "registration": "2024002",
                "name": "Maria Silva",
                "email": "maria@example.com",
                "role": models.UserRole.student,
                "password": "senha123"
            },
            {
                "registration": "PROF001",
                "name": "Professor Paulo Lemes",
                "email": "paulo@example.com",
                "role": models.UserRole.teacher,
                "password": "senha123"
            },
            {
                "registration": "SUPORTE",
                "name": "Atendimento UCB",
                "email": "atendimento@ucb.br",
                "role": models.UserRole.coordinator,
                "password": "senha123"
            }
        ]
        
        created_users = []
        for user_data in users_data:
            # CORREÇÃO: Verificar se o utilizador já existe por matrícula OU por e-mail
            existing = db.query(models.User).filter(
                or_(
                    models.User.registration == user_data["registration"],
                    models.User.email == user_data["email"]
                )
            ).first()
            
            if not existing:
                user = models.User(
                    registration=user_data["registration"],
                    name=user_data["name"],
                    email=user_data["email"],
                    passwordHash=get_password_hash(user_data["password"]),
                    role=user_data["role"],
                    accessStatus=models.AccessStatus.active
                )
                db.add(user)
                # Usar flush para obter o ID do utilizador antes do commit final
                db.flush() 
                created_users.append(user)
                print(f"✅ Utilizador criado: {user.name}")
            else:
                created_users.append(existing)
                print(f"ℹ️  Utilizador já existe: {existing.name}")
        
        db.commit()
        
        print("\n🔄 Criando conversas de teste...")
        
        # --- Conversa 1: Atendimento (suporte) ---
        # Verificar se a conversa já existe para evitar duplicados
        conv1_participants = {created_users[0], created_users[3]}
        conv1 = db.query(models.Conversation).filter(
            models.Conversation.type == models.ConversationType.support,
            *[models.Conversation.participants.any(id=p.id) for p in conv1_participants]
        ).first()

        if not conv1:
            conv1 = models.Conversation(
                title="Atendimento UCB",
                type=models.ConversationType.support,
                participants=[created_users[0], created_users[3]]
            )
            db.add(conv1)
            db.flush()
            
            # Criar hierarquia de canais
            channel1 = models.Channel(name="Channel-Atendimento", conversationId=conv1.id)
            db.add(channel1)
            db.flush()
            
            subchannel1 = models.Subchannel(name="Geral", parentChannelId=channel1.id)
            db.add(subchannel1)
            db.flush()
            
            # Adicionar mensagens apenas se a conversa for nova
            messages_conv1 = [
                {"content": "Olá! Bem-vindo ao atendimento UCB. Como posso ajudá-lo?", "authorId": created_users[3].id, "timestamp": datetime.utcnow() - timedelta(hours=2)},
                {"content": "Oi! Gostaria de informações sobre o calendário académico.", "authorId": created_users[0].id, "timestamp": datetime.utcnow() - timedelta(hours=1, minutes=55)},
                {"content": "Claro! O calendário está disponível na plataforma. Pode acedê-lo pelo menu principal.", "authorId": created_users[3].id, "timestamp": datetime.utcnow() - timedelta(hours=1, minutes=50)}
            ]
            
            for msg_data in messages_conv1:
                msg = models.Message(content=msg_data["content"], subchannelId=subchannel1.id, authorId=msg_data["authorId"], timestamp=msg_data["timestamp"], isRead=False)
                db.add(msg)
            
            print("✅ Conversa de Atendimento criada")
        else:
            print("ℹ️  Conversa de Atendimento já existe")

        # --- Conversa extra entre ID 11 e ID 37 ---
        print("\n🔄 Criando conversa extra...")
        user_11 = db.query(models.User).filter(models.User.id == 11).first()
        user_37 = db.query(models.User).filter(models.User.id == 37).first()

        if user_11 and user_37:
            # Verifica se uma conversa direta entre eles já existe
            existing_conv = db.query(models.Conversation).filter(
                models.Conversation.type == models.ConversationType.direct,
                models.Conversation.participants.contains(user_11),
                models.Conversation.participants.contains(user_37)
            ).first()

            if not existing_conv:
                conv_extra = models.Conversation(
                    title=f"Conversa entre {user_11.name} e {user_37.name}",
                    type=models.ConversationType.direct,
                    participants=[user_11, user_37]
                )
                db.add(conv_extra)
                db.flush()

                channel_extra = models.Channel(name=f"Channel-Conv-{conv_extra.id}", conversationId=conv_extra.id)
                db.add(channel_extra)
                db.flush()

                subchannel_extra = models.Subchannel(name="Geral", parentChannelId=channel_extra.id)
                db.add(subchannel_extra)
                db.flush()

                messages_extra = [
                    {"content": "Olá, sou o administrador. Como posso ajudar?", "authorId": user_11.id, "timestamp": datetime.utcnow() - timedelta(minutes=30)},
                    {"content": "Tenho uma dúvida sobre as minhas notas.", "authorId": user_37.id, "timestamp": datetime.utcnow() - timedelta(minutes=28)},
                ]
                for msg_data in messages_extra:
                    msg = models.Message(content=msg_data["content"], subchannelId=subchannel_extra.id, authorId=msg_data["authorId"], timestamp=msg_data["timestamp"], isRead=False)
                    db.add(msg)
                
                print(f"✅ Conversa extra entre {user_11.name} (ID: 11) e {user_37.name} (ID: 37) criada.")
            else:
                print("ℹ️  Conversa extra entre ID 11 e 37 já existe.")
        else:
            print("⚠️  Não foi possível criar a conversa. Utilizador com ID 11 ou 37 não encontrado.")


        db.commit()
        print("\n✅ Dados de teste criados com sucesso!")
        print("\n📝 Credenciais de teste:")
        print("   Gabriel Aluno: 2024001 / senha123")
        print("   Maria Silva: 2024002 / senha123")
        print("   Professor Paulo: PROF001 / senha123")
        print("   Atendimento: SUPORTE / senha123")
        
    except Exception as e:
        print(f"\n❌ Erro ao criar dados de teste: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 Iniciando criação de dados de teste para o Chat...\n")
    create_test_data()

