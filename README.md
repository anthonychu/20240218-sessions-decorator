```python
from azure_container_apps import SessionsPool


pool = SessionsPool(
    subscription_id='ef6e1243-d48a-417e-8e6d-40cd96e110fd',
    resource_group='test-sessions',
    session_pool='antchu-test',
    sessions_api_base_url='https://northcentralusstage.acasessions.io/',
)

with pool.session(session_id='12345') as session:

    session.file('orders.csv').upload(os.path.join(os.getcwd(), 'orders.csv'))
    session.execute('import pandas as pd')
    session.execute('orders = pd.read_csv("/mnt/data/orders.csv")')
    session.execute('total = orders["amount"].sum()')
    total_sales = session.execute('return total')
```



```python
from azure_container_apps import SessionsPool


pool = SessionsPool(
    subscription_id='ef6e1243-d48a-417e-8e6d-40cd96e110fd',
    resource_group='test-sessions',
    session_pool='antchu-test',
    sessions_api_base_url='https://northcentralusstage.acasessions.io/',
)

session = pool.session(session_id='12345')

orig_file = session.file('orders.csv').upload(os.path.join(os.getcwd(), 'orders.csv'))

@session.remote
def calculate_total_sales(input_filename):
    import pandas as pd
    orders = pd.read_csv(os.path.join('/mnt/data', input_filename))
    total = orders['amount'].sum()

    sorted_orders = orders.sort_values('amount')
    sorted_orders.to_csv(os.path.join('/mnt/data', 'sorted_orders.csv'))


total_sales = calculate_total_sales(orig_file.filename)
local_sorted_file_path = os.path.join(os.getcwd(), 'sorted_orders.csv')
sorted_file = session.file('sorted_orders.csv').download(local_sorted_file_path)

with open(local_sorted_file_path, 'r') as f:
    print(f.read())
```