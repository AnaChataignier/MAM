import random
from faker import Faker
from staff.models import Cliente,  OrdemDeServico
from authentication.models import Endereco
from django.contrib.auth.models import Group
import pytz

fake = Faker(["pt_BR"])
staff_group = Group.objects.get(name="Staff")
tecnico_group = Group.objects.get(name="Técnico")


def create_cliente_and_endereco():
    # Crie um endereço falso usando o Faker
    endereco = Endereco.objects.create(
        cep="22010-010",
        rua=fake.street_name(),
        bairro=fake.neighborhood(),
        cidade=fake.city(),
        estado=fake.state(),
        numero=fake.building_number(),
        complemento="Qualquer coisa",
    )

    # Crie um cliente falso usando o Faker
    cliente = Cliente.objects.create(
        nome=fake.name(),
        rg=fake.ssn(),
        endereco=endereco,
        telefone1=fake.phone_number(),
        telefone2=fake.phone_number(),
    )

    previsao_chegada = fake.future_datetime(
        end_date="+30d", tzinfo=pytz.timezone("America/Sao_Paulo")
    )
    previsao_execucao = fake.future_datetime(
        end_date="+60d", tzinfo=pytz.timezone("America/Sao_Paulo")
    )
    ordem = OrdemDeServico.objects.create(
        ticket=fake.unique.random_int(min=1111111, max=9999999),
        tecnico=random.choice(tecnico_group.user_set.all()),
        staff=random.choice(staff_group.user_set.all()),
        descricao=fake.text(max_nb_chars=100),
        previsao_chegada=previsao_chegada,
        previsao_execucao=previsao_execucao,
        material="Aqui se coloca os materiais que serão usados",
        equipamento="Aqui se coloca os equipamentos que serão usados",
        data_criacao=fake.past_datetime(start_date="-30d"),
        cliente=cliente,
        atividade="Manutenção",
        status_tecnico="Aguardando Início",
    )


def run():
    for _ in range(100):
        create_cliente_and_endereco()


if __name__ == "__main__":
    run()
