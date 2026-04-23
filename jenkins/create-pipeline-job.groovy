/*
 * Jenkins Pipeline Seed Script
 * ────────────────────────────
 * Paste this into Jenkins → Manage Jenkins → Script Console → Run
 * It creates the "Digital Smart Finance Tracker v5" pipeline job
 * pointing at the GitHub repo automatically.
 *
 * Pre-requisites (install via Manage Jenkins → Plugins):
 *   - Git Plugin
 *   - Pipeline Plugin
 *   - Docker Pipeline Plugin
 */

import jenkins.model.*
import org.jenkinsci.plugins.workflow.job.WorkflowJob
import org.jenkinsci.plugins.workflow.cps.CpsScmFlowDefinition
import hudson.plugins.git.*
import hudson.triggers.SCMTrigger

def jenkins   = Jenkins.get()
def jobName   = "digital-smart-finance-tracker-v5"
def repoUrl   = "https://github.com/aftonis/digital-smart-finance-tracker-v5.git"
def branch    = "*/main"

// ── Remove existing job (idempotent re-run) ──────────────────────────────────
def existing = jenkins.getItem(jobName)
if (existing) {
    existing.delete()
    println "Deleted existing job: ${jobName}"
}

// ── Create pipeline job ───────────────────────────────────────────────────────
def job = jenkins.createProject(WorkflowJob, jobName)
job.setDescription(
    "Quartet Protocol — Mission Charlie: Analyst + Reporting Engine\\n" +
    "ADLC Pipeline: Plan → Design → Execute → Deploy\\n" +
    "Repo: ${repoUrl}"
)

// Point at the Jenkinsfile in the repo root
def scm = new GitSCM(
    GitSCM.createRepoList(repoUrl, null),
    [new BranchSpec(branch)],
    false, [],
    null, null, []
)
job.setDefinition(new CpsScmFlowDefinition(scm, "Jenkinsfile"))

// Poll GitHub every 5 minutes for new commits (H/5 * * * *)
job.addTrigger(new SCMTrigger("H/5 * * * *"))

job.save()
jenkins.reload()

println "✅ Pipeline job '${jobName}' created successfully."
println "   Repo  : ${repoUrl}"
println "   Branch: ${branch}"
println "   Trigger: Poll SCM every 5 minutes"
println ""
println "Next: click '${jobName}' → 'Build Now' for the first run."
