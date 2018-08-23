# catalog_project

This is a library catalog for the Udacity backend module project.

The purpose of the project is to build a CRUD application using Flask, sqlalchemy
and 3rd party authentication.

## What can you do with the catalog?

You can log in with Google and add, edit or delete your own books and peruse the books that
other people have added. The catalog is sorted into genres. Book information includes title,
author, synopsis, cover image and the person who added the book to the catalog.

## Running the program

The catalog is designed to be run via the Udacity linux virtual machine command line.

You can install VirtualBox via this [link](https://www.virtualbox.org/wiki/Downloads) and vagrant, the command line utility to manage the virtual machine [here](https://www.vagrantup.com/downloads.html). 
  
 * Create a folder to store the files for this project and then open the folder with the terminal.
 * Save Vagrantfile in your vagrant folder.
 * Type `vagrant init ubuntu/trusty64` to tell Vagrant what kind of Linux VM you want to run
 * Run the virtual machine by running `vagrant up`and `vagrant ssh` to log in.
 * `cd` into your folder and load the databade by typing `python database_setup.py` into the shell
 * Run `python populate_database.py` to add the genres to the catalog.
 * The catalog does not yet have any books in it, if you'd like to preload some books with a 
  dummy user then run `python populate_with_books.py`
 * Otherwise, run the catalog by typing `python catalog.py`. The catalog can be utilised by visiting
  http://localhost:8000/login or http://localhost:8000/genres
 * JSON data can be accessed for any book by adding "/JSON" to the url of the book information pages
