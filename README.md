genelist
====

Web application for creating and managing gene lists. The purpose of this
application is to store lists of genes and any evidence for their
inclusion. Evidence could be a publication or a comment from an
authenticated user.


This also serves as a demonstration of using Vagrant and Docker for
application development. This app is developed using Python/Flask and
Postgresql. The web app and database run in separate Docker containers
that are managed by Vagrant in a VM. This makes the dev environment easy
to setup for multiple developers.
