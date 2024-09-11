### Hexlet tests and linter status:
[![Actions Status](https://github.com/VAN4SH/python-project-83/actions/workflows/hexlet-check.yml/badge.svg)](https://github.com/VAN4SH/python-project-83/actions)

## [Анализатор страниц](https://python-project-83-jokk.onrender.com)
### Cайт, который анализирует указанные страницы на SEO-пригодность по аналогии с PageSpeed Insights

### Установка проекта

1. Необходимо склонировать репозиторий

```shell
git clone https://github.com/VAN4SH/python-project-83.git
```

2. Перейти на сайт [Render.com](https://render.com/) и создать новый проект

3. Добавить на новый проект переменные окружения такие как:

```shell
DATABASE_URL
POETRY_VERSION
PYTHON_VERSION
SECRET_KEY #Необходимо сгенерировать самостоятельно
```

4. Прописать команды для сборки и старта проекта

```shell
make build
make start
```

5. Запустить деплой проекта
