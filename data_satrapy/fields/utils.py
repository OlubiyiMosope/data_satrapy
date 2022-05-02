from flask import flash, url_for, redirect
from data_satrapy import db
from data_satrapy.models import Field


# To list all the fields in the database (in alphabetical order)
def list_subjects():
    fields = [field.subject for field in Field.query.all()]
    fields.sort()

    field_ids = []
    for field in fields:
        field = Field.query.filter_by(subject=field).first()
        field_ids.append(field.id)

    return list(zip(field_ids, fields))


def delete_field(subject_id):
    field = Field.query.get_or_404(subject_id)
    flash(f"You have deleted the field '{field.subject}'!", "success")
    db.session.delete(field)
    db.session.commit()
    return redirect(url_for("fields.add_field"))
