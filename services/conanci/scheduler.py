from conanci.config import app, db
from conanci import database

logger = app.app.logger


def process_commits():
    logger.info("Start processing commits")

    new_builds = False
    commits = database.Commit.query.filter_by(status=database.CommitStatus.new)
    profiles = database.Profile.query.all()
    for commit in commits:
        logger.info("Process commit '%s' of repo '%s'", commit.sha[:7], commit.repo.url)
        for profile in profiles:
            new_builds = True
            logger.info("Schedule build for '%s' with profile '%s'", commit.sha[:7], profile.name)
            build = database.Build()
            build.profile = profile
            build.commit = commit
            build.status = database.BuildStatus.new
            db.session.add(build)
        logger.info("Set commit '%s' to 'building'", commit.sha[:7])
        commit.status = database.CommitStatus.building
        db.session.commit()

    if new_builds:
        logger.info("Finish processing commits with *new* builds")
    else:
        logger.info("Finish processing commits with *no* builds")

    return new_builds
