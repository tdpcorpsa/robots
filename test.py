import click
import inquirer

@click.command()
def select_database():
    options = [
        {'name': 'Test Database', 'value': 'test'},
        {'name': 'Production Database', 'value': 'production'}
    ]
    questions = [
        inquirer.List('database', message='Select database', choices=[option['name'] for option in options], carousel=True)
    ]
    answers = inquirer.prompt(questions)

    selected_name = answers['database']
    selected_value = next(option['value'] for option in options if option['name'] == selected_name)

    # Use the selected_value variable to perform further actions
    if selected_value == 'test':
        print('Selected test database')
        # Perform test database operations
    elif selected_value == 'production':
        print('Selected production database')
        # Perform production database operations
    else:
        print('Invalid option')

if __name__ == '__main__':
    select_database()
