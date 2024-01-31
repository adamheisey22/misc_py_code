Forking a repository in GitLab without using the UI's fork button can be achieved by manually creating a copy of the repository and pushing it to a new repository under your account. This process involves cloning the original repository to your local machine, creating a new repository on GitLab, and then pushing the cloned content to this new repository. Here's how you can do it step-by-step:

1. **Clone the Original Repository**: First, you need to clone the repository you want to fork to your local machine. Use the Git command line tool for this purpose. Replace `original_repository_url` with the actual URL of the repository you wish to fork.

    ```bash
    git clone --bare original_repository_url
    ```

    The `--bare` option is used to clone the repository without checking out a working copy, which is useful for creating a mirror of the original repository.

2. **Create a New Repository on GitLab**: Go to GitLab and create a new repository where you will host the fork. This can be done through the GitLab interface. Remember the URL of the new repository.

3. **Push to the New Repository**: Change into the directory of the cloned repository on your local machine, then push it to your new repository on GitLab using the following commands. Replace `new_repository_url` with the URL of the new GitLab repository you created.

    ```bash
    cd original_repository_name.git
    git push --mirror new_repository_url
    ```

    The `--mirror` option ensures that all refs (like branches and tags) along with the commits are pushed to the new repository.

4. **Remove the Local Copy of the Repository**: After successfully pushing the repository to GitLab, you can remove the local copy of the repository if you want, as it's no longer needed.

    ```bash
    cd ..
    rm -rf original_repository_name.git
    ```

This method effectively "forks" the repository without using the GitLab UI's fork feature. It's particularly useful when you want to fork a repository but need more control over the process or when dealing with repositories where the fork option is disabled or not available.