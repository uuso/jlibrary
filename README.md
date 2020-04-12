# jlibrary
Library app to help me organize my book collection

Database principles:
----
The main objects are **Author, Story, Book**, secondary are _Publisher, Genre_:
  - **Author** can write a **Story** (can have several **Genres**);
  - **Story**/Stories can be published in **Book** by **Publisher**;
  - **Book** can be a part of _multivolume_ **Story**
  - Multivolume **Stories** can be a MultivolumeCycle or a MultivolumeStory
#### Multivolumes are:
  - _"MVS"_ :: **Author**'s **Story** _(root)_ of multiple volumes (**Book**). Each **Book** has no **Stories** inside, but it's *multivolume* field refers to the root **Story**
  - _"MVC"_ :: **Story** _(root)_ as the series of **Book**s *(book cycle)* with or without a certain **Author**. Each **Book** has it's own **Story**/Stories inside and it's *multivolume* field refers to the root **Story**

_"MVF"_ **Story** is a **Story** that shouldn't be used as a multivolume - _Multivolume**F**alse_
#### Multivolume principles:
  1. The root **Story**'s _is_multivolume_ field must be set to _"MVS"_ or _"MVC"_ (**S**tory and **C**ycle)
  2. The **Books** of _multivolume_ must have (_"MVS"_, _"MVC"_) in their _has_multivolume_ field.

Current state:
----
  - created DB structure, models, admin-panel
