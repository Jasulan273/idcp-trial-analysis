import jenkins.model.Jenkins
import hudson.security.HudsonPrivateSecurityRealm
import hudson.security.FullControlOnceLoggedInAuthorizationStrategy
import hudson.plugins.git.GitSCM
import hudson.plugins.git.BranchSpec
import hudson.plugins.git.UserRemoteConfig
import org.jenkinsci.plugins.workflow.job.WorkflowJob
import org.jenkinsci.plugins.workflow.cps.CpsScmFlowDefinition
import jenkins.model.JenkinsLocationConfiguration

def j = Jenkins.get()
def passwordFile = new File('/run/secrets/admin_password')
if (!passwordFile.exists()) throw new IllegalStateException('Admin password file is required')
def realm = new HudsonPrivateSecurityRealm(false)
realm.createAccount('assignment-admin', passwordFile.text.trim())
j.setSecurityRealm(realm)
def strategy = new FullControlOnceLoggedInAuthorizationStrategy()
strategy.setAllowAnonymousRead(true)
j.setAuthorizationStrategy(strategy)
j.setNumExecutors(1)
JenkinsLocationConfiguration.get().setUrl('http://127.0.0.1:8085/')
def job = j.getItem('idcp-trial-analysis-ci')
if (job == null) job = j.createProject(WorkflowJob, 'idcp-trial-analysis-ci')
def remote = new UserRemoteConfig('https://github.com/Jasulan273/idcp-trial-analysis.git', null, null, null)
def scm = new GitSCM([remote], [new BranchSpec('*/main')], false, [], null, null, [])
def definition = new CpsScmFlowDefinition(scm, 'Jenkinsfile')
definition.setLightweight(true)
job.setDefinition(definition)
job.setDescription('Assignment 5: Python unit tests, Docker build and research analysis artifacts. Synthetic example only.')
job.save()
j.save()
