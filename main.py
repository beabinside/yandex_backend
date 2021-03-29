from flask import Flask, request
from flask_restful import Api, Resource
from flask_sqlalchemy import SQLAlchemy
import json


HOST = '0.0.0.0'
PORT = 8080

app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

# db.drop_all()


class CouriersModel(db.Model):
    courier_id = db.Column(db.Integer, primary_key=True)
    courier_type = db.Column(db.String(15), nullable=False)
    regions = db.Column(db.JSON, nullable=False)
    working_hours = db.Column(db.JSON, nullable=False)
    rating = db.Column(db.Integer, nullable=True)
    earnings = db.Column(db.Integer, nullable=True)


class OrdersModel(db.Model):
    order_id = db.Column(db.Integer, primary_key=True)
    courier_id = db.Column(db.Integer, nullable=True)
    weight = db.Column(db.Integer, nullable=False)
    region = db.Column(db.Integer, nullable=False)
    delivery_hours = db.Column(db.JSON, nullable=False)
    complete_time = db.Column(db.String(25), nullable=True)


def timestamps_intersect(timestamp1, timestamp2):
    start1, end1 = timestamp1.split('-')
    start1_hours, start1_minutes = [int(i) for i in start1.split(':')]
    end1_hours, end1_minutes = [int(i) for i in end1.split(':')]
    start2, end2 = timestamp2.split('-')
    start2_hours, start2_minutes = [int(i) for i in start2.split(':')]
    end2_hours, end2_minutes = [int(i) for i in end2.split(':')]
    if start1_hours < end1_hours:
        end1_hours += 24
    if start2_hours < end2_hours:
        end2_hours += 24
    if not (end1_hours < start2_hours or (end1_hours == start2_hours and end1_minutes < start2_minutes)) and \
            not (end2_hours < start1_hours or (end2_hours == start1_hours and end2_minutes < start1_minutes)):
        return True
    return False


db.create_all()


class Couriers(Resource):
    # @marshal_with(courier_fields)
    def get(self, cour_id):
        res = CouriersModel.query.filter_by(courier_id=cour_id).first()
        return {"courier_id": res.courier_id,
                "courier_type": res.courier_type,
                "regions": res.regions,
                "working_hours": res.working_hours
                }, 400

    def post(self):
        args = request.get_json(force=True)
        errors = {"validation_error": {"couriers": []}}
        success = {"couriers": []}
        for courier in args["data"]:
            check = CouriersModel.query.filter_by(courier_id=courier["courier_id"]).first()
            if not check:
                cour_ = CouriersModel(courier_id=courier["courier_id"], courier_type=courier["courier_type"],
                                      regions=courier["regions"], working_hours=courier["working_hours"])
                db.session.add(cour_)
                success["couriers"].append({"id": courier["courier_id"]})
            else:
                errors["validation_error"]["couriers"].append({"id": courier["courier_id"]})
        db.session.commit()
        if len(errors["validation_error"]["couriers"]):
            return errors, 400
        return success, 201

    def patch(self, cour_id):
        args = request.get_json(force=True)
        check = CouriersModel.query.filter_by(courier_id=cour_id).first()
        if not check:
            return "Bad request", 400
        if "courier_type" in args:
            check.courier_type = args["courier_type"]
        elif "regions" in args:
            check.region = args["regions"]
        else:
            check.working_hours = args["working_hours"]
        db.session.commit()
        return {"courier_id": check.courier_id,
                "courier_type": check.courier_type,
                "regions": check.regions,
                "working_hours": check.working_hours
                }, 400


class Orders(Resource):
    def post(self, command):
        args = request.get_json(force=True)
        if command == "":
            errors = {"validation_error": {"orders": []}}
            success = {"orders": []}
            for order in args["data"]:
                check = OrdersModel.query.filter_by(courier_id=order["order_id"]).first()
                if not check:
                    order_ = OrdersModel(order_id=order["order_id"], weight=order["weight"], region=order["region"],
                                         delivery_hours=order["delivery_hours"])
                    db.session.add(order_)
                    success["orders"].append({"id": order["order_id"]})
                else:
                    errors["validation_error"]["orders"].append({"id": order["order_id"]})
            db.session.commit()
            if len(errors["validation_error"]["orders"]):
                return errors, 400
            return success, 201
        elif command == "assign":
            courier_id = args["courier_id"]
            courier = CouriersModel.query.filter_by(courier_id=courier_id).first()
            if courier.courier_type == "foot":
                courier_max_weight = 10
            elif courier.courier_type == "bike":
                courier_max_weight = 15
            else:
                courier_max_weight = 50
            suitables = db.session.query(OrdersModel) \
                .filter(OrdersModel.weight <= courier_max_weight) \
                .filter(OrdersModel.region in courier.regions) \
                .filter(True in [True in [timestamps_intersect(courier.working_hours[i], OrdersModel.delivery_hours[j])
                                 for j in range(len(list(OrdersModel)))]
                                 for i in range(len(list(courier.working_hours)))])
            print(type(suitables))

        elif command == "complete":
            courier_id = args["courier_id"]
            order_id = args["order_id"]
            complete_time = args["complete_time"]
            check = OrdersModel.query.filter_by(order_id=order_id).first()
            if not check or check.courier_id != courier_id:
                return "Bad request", 400
            check.complete_time = complete_time
            check.courier_id = None
            db.session.commit()
            return {"order_id": order_id}, 200


api.add_resource(Couriers, "/couriers", "/couriers/<int:cour_id>")
api.add_resource(Orders, "/orders", "/orders/<string:command>")


if __name__ == "__main__":
    app.run(debug=True, host=HOST, port=PORT)
