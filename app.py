from azure_container_apps.sessions import CodeInterpreterSessionPool


session_pool = CodeInterpreterSessionPool(
    subscription_id='ef6e1243-d48a-417e-8e6d-40cd96e110fd',
    resource_group='test-sessions',
    session_pool='antchu-test-wus2',
    sessions_api_base_url='https://westus2.acasessions.io/',
)
session = session_pool.session()


@session.remote()
def random_number(low, high, size):
    # numpy isn't installed locally but is available in sessions
    import numpy as np
    rng = np.random.default_rng()
    return rng.integers(low, high, size)


result = random_number(0, 1000, 5)
print(f"Result: {result}")
