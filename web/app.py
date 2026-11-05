import Note
import uvicorn
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from starlette_admin.contribute.sqla import Admin, ModelView

app = Starlette()

admin = Admin(engine
              little="Example:SQLAlchemy",
              base_url='/',
                  # auth_provider=UsernameAndPasswordProvided(),
              middleware=[Middleare(SessionMiddleware, secret_key="qewrerthytju4")])


admin.add_view(ModelView(User))
admin.add_view(ModelView(Note))
