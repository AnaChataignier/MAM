STATE_CHOICES = [
    ("AC", "Acre"),
    ("AL", "Alagoas"),
    ("AP", "Amapá"),
    ("AM", "Amazonas"),
    ("BA", "Bahia"),
    ("CE", "Ceará"),
    ("DF", "Distrito Federal"),
    ("ES", "Espírito Santo"),
    ("GO", "Goiás"),
    ("MA", "Maranhão"),
    ("MT", "Mato Grosso"),
    ("MS", "Mato Grosso do Sul"),
    ("MG", "Minas Gerais"),
    ("PA", "Pará"),
    ("PB", "Paraíba"),
    ("PR", "Paraná"),
    ("PE", "Pernambuco"),
    ("PI", "Piauí"),
    ("RJ", "Rio de Janeiro"),
    ("RN", "Rio Grande do Norte"),
    ("RS", "Rio Grande do Sul"),
    ("RO", "Rondônia"),
    ("RR", "Roraima"),
    ("SC", "Santa Catarina"),
    ("SP", "São Paulo"),
    ("SE", "Sergipe"),
    ("TO", "Tocantins"),
]

STATUS_CHOICES = (
    ("Aguardando", "Aguardando"),
    ("Atenção", "Atenção"),
    ("Urgente", "Urgente"),
    ("Concluído", "Concluído"),
)

ACTIVITY_CHOICES = (
    ("Manutenção", "Manutenção"),
    ("Ativação", "Ativação"),
    ("Logística", "Logística"),
    ("Teste Interno", "Teste Interno"),
)

TECNICAL_CHOICES = (
    ("Aguardando Aceite", "Aguardando Aceite"),
    ("À Caminho", "À Caminho"),
    ("No Local", "No local"),
    ("Finalizado", "Finalizado"),
)
