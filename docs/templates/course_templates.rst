Course Templates
================

.. role:: sql(code)
    :language: sql

Course templates are a collection of abstract sql statements. These are used to create the courses. First the abstract
statements become concrete and then a task is generated for this statement.

For example the course template contains :sql:`SELECT * FROM [table1];`. This generates something like
:sql:`SELECT * FROM books;` for a library database. Then in the final step the task *"Select every column
from the table books"* is generated.

.. toctree::
   :maxdepth: 2
   :caption: Course Templates

   course_template_1
   course_template_2
   course_template_3
   course_template_4
   course_template_5
   course_template_6