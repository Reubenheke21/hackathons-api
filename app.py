from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
app = Flask(__name__)
ma = Marshmallow(app)


#what dbms + db adapter + db_user + password + host:port + dbname
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql+psycopg2://reuben:Rhiannon31@localhost:5432/hackathon_db_flask"

#create the database instance
db = SQLAlchemy(app)

@app.cli.command("create")
def create_table():
    db.create_all()
    print("tables created")

@app.cli.command("seed")
def seed_database():
    project1 = Project(
        title = 'Brisbane Traffic Solver', 
        repository = 'https://github.com/traffic_team/traffic_solver',
        description = 'description goes here...'
    )
    db.session.add(project1)
    db.session.commit()

    project2 = Project(
        title = 'Sustainability coding board game', 
        repository = 'https://github.com/ca_team/coding_board_game',
        description = 'description goes here...'
    )
    db.session.add(project2)
    db.session.commit()
    print("tables seeded")

@app.cli.command('drop')
def drop_table():
    db.drop_all()
    print("tables dropped")

class Project(db.Model):
    __tablename__ = "projects"

    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String())
    repository = db.Column(db.String())
    description = db.Column(db.String())

class ProjectSchema(ma.Schema):
    class Meta:
        fields = ("id", "title", "repository", "description")

projects_schema = ProjectSchema(many=True)
project_schema = ProjectSchema()

@app.route("/")
def welcome():
    return "Welcome students to hackathon"

#app.route('/projects' methods=["GET"]) 
#@app.route("/projects") #always executed by a get method unless you input it by methods=["GET"]
@app.get('/projects')
def get_projects():
    #prepare the query to get data
    stmt = db.select(Project)
    #get the data
    projects = db.session.scalars(stmt)
    #convert the db data into something readable by python
    result = projects_schema.dump(projects)
    return result

@app.get('/projects/<int:id>/')
def get_project_by_id(id):
    #prepare the query to get data
    stmt = db.select(Project).filter_by(id = id)
    #get the data
    project = db.session.scalar(stmt)
    #convert the db data into something readable by python
    

    if project:
        return project_schema.dump(project)
    else:
        return {'error' : f'Project not found with that id {id}'}, 404


@app.post('/projects')
def create_project():
    #print(request.json)
    project_fields = project_schema.load(request.json)
    new_project = Project(
        title = project_fields["title"], 
        repository = project_fields["repository"],
        description = project_fields["description"]
        )
    db.session.add(new_project)
    db.session.commit()
    return project_schema.dump(new_project), 201
