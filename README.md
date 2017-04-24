# Brain Drain Blog Site
Brain Drain is a multi-user blog, hosted on Google App Engine that enables a user to post, like, and event leave comments on each other's blog post. In addition, it contains a user registration and authentication system, complete with securely stored salted and hashed user credentials utilizing SHA256. Further, secure session tracking is implemented via cookies which are uniquely assigned to each user upon successful authentication into the web application.

## Getting Started
New users can open their browser and navigate to [Brain Drain](https://splendid-unison-160018.appspot.com/signup).  They will be prompted for a user name, password and an optional email address.  After successfully entering these items, the user will be redirected to the blog home page.  Here the user can browse blog post by others, like a blog post made by someone else, or even leave a comment on a blog post.

Users can leave a new blog post by clicking on the "What's on you mind?" button in the top left corner, under the Brain Drain logo. Clicking this will take the user to the new blog post page where they fill out the subject out their blog post and the the body of what they want to post. Clicking "submit" on this page will submit the blog post and take the user to a permalink for their newly created post.  From here, you can click the Brain Drain logo in the top left of the page to go back to the home page and see your new blog post displayed along side others.

If you wish to change something in your post, you can click the edit button in the top right of the blog post. This will take you to the edit page where you can change your blog post.  Clicking submit will save the change and take you to the permalink for your edited post.  You can also delete your blog post by clicking the delete button in the top right of your post.  Clicking this will take you to the delete confirmation page.  Clicking the delete button on this page will delete your blog post and take you back to the home page.

Now that you have posted your first blog, you can check out the post of others and leave a comment if you wish. By clicking the comment button in the lower right of any blog post, you will be directed to a comment page. Type in your comment and click the submit button. You will see your comment appear below the the blog post.
You can also edit or delete your comment by clicking the edit or delete button on the bottom right hand side of your comment.  Clicking the edit button will take you to the edit page where you can change your comment. Clicking submit will save the change and take you back to the home page.  Clicking the delete button will take you to the delete confirmation page. If you click delete here, your comment will be deleted.

Don't forget to like the post as well, clickin the like button in the bottom right of any post will like it if you haven't already and unlike it if you have already like it

You may logout of the site by clicking the "Logout" button in the top right of page.  Now that you are a registered user, you can simply sign in next time without creating an account at [Brain Drain Login](https://splendid-unison-160018.appspot.com/login).

## Running the App Locally
Runninng the Brain Drain application on your local machine requires downloading and installing the Google App Engine SDK, which can be done [here](https://cloud.google.com/appengine/docs/standard/python/download). After installing the SDK, install the gcloud component by running `gcloud components install app-engine-python` in your terminal. Once you have the SDK and gcloud components installed, you can run the app locally by navigating to directory where you have downloaded Brain Drain and running `dev_appserver.py app.yaml`.  This will run the application's app.yaml file and launch the development server on your machine, which you can acess at `http://localhost:8080/`.

If you would like to deploy your own version of Brain Drain, you can do so by navigating to [Google's Developer Console](https://console.cloud.google.com/home/dashboard?project=splendid-unison-160018) and creating a new project. Once you have the project ID, simply run `gcloud app deploy --project [PROJECT ID]` and you can navigate to your app using any web browser at `[PROJECT ID].appspot.com`.

## License
The content of Brain Drain is licensed under a MIT License.

MIT License

Copyright (c) 2017 Dennis Flannigan

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
