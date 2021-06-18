from invoke import task

@task
def test(c):
    c.run('python -m unittest discover -s tests -p "test_*.py"')
