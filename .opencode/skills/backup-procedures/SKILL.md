# Backup Procedures Skill

## Descrição
Esta skill fornece procedimentos e melhores práticas para criar backups seguros do repositório English JATEL antes de realizar alterações no código, configuração ou conteúdo.

## Quando Usar
Use esta skill sempre que planejar:
- Modificar arquivos de código fonte
- Alterar arquivos de configuração
- Editar conteúdo de dados (grammar.json, memhack.json, etc.)
- Executar scripts de migração
- Realizar merges de branches
- Aplicar atualizações de dependências

## Procedimentos

### 1. Perguntar se deseja a fazer o backup
Perguntar Primeiro  se deseja realizar o backup , antes de proceseguir 

### 2. Backup Local Completo
Antes de qualquer alteração, crie um backup completo:

```bash
# Criar diretório de backup (se não existir)
mkdir -p repo-backup

# Copiar todo o repositório excluindo o próprio backup
rsync -av --exclude='repo-backup/' . ./repo-backup/
```

### 3. Verificação do Backup
Verifique se o backup foi criado corretamente:

```bash
# Comparar contagem de arquivos
find . -type f | ! -path "./repo-backup/*" | wc -l
find ./repo-backup -type f | wc -l
```

### 4. Configurar .gitignore
Certifique-se de que o diretório de backup está no .gitignore:

```
repo-backup/**
```

### 5. Restaurando do Backup (se necessário)
```bash
# Restaurar arquivo específico
cp -r repo-backup/caminho/para/arquivo .

# Restaurar todo o repositório (use com cautela!)
rsync -av --exclude='repo-backup/' ./repo-backup/ ./
```

## Melhores Práticas

1. **Sempre Pergunta se vai desejar fazer o backup** 
2. **Sempre faça backup primeiro** - Nunca inverta esta ordem
3. **Valide o backup** - Confirme que os arquivos foram copiados corretamente
4. **Inclua dados de usuário** - Lembre-se de backup em `backend/data/`
5. **Mantenha backups recentes** - Faça novo backup antes de cada sessão de trabalho significativa
5. **Documente alterações** - Anote o que você planeja fazer antes de fazer o backup

## Verificação de Pré-condições
Antes de executar qualquer tarefa de modificação, verifique:
- [ ] Backup recente criado
- .gitignore contém `repo-backup/**`
- Espaço em disco suficiente disponível
- Permissões de leitura/escrita confirmadas

## Exemplos de Uso

### Antes de modificar engine.py:
```bash
mkdir -p repo-backup
rsync -av --exclude='repo-backup/' . ./repo-backup/
# Validar backup...
# Então proceder com as alterações em engine.py
```

### Antes de atualizar grammar.json:
```bash
# Mesmo procedimento de backup acima
# Depois editar grammar.json com confiança
```

## Integração com Outras Skills
Esta skill deve ser usada como **pré-requisito** para:
- english-jatel (modificações no core)
- english-jatel-render (deploy)
- Qualquer skill que implique em modificação de arquivos

## Limitações
- Não substitui backups remotos ou versionamento Git
- Destinado a proteção contra erros humanos locais durante desenvolvimento
- Não inclui backup automático de banco de dados externos (se aplicável)
