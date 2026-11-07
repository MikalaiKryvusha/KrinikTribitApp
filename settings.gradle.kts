// Krinik Tribit - Gradle settings. One module: :app (the Compose app that talks to Tribit speakers).
pluginManagement {
    repositories {
        google()
        mavenCentral()
        gradlePluginPortal()
    }
}
dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {
        google()
        mavenCentral()
        // JitPack for FreeDroidWarn only (KAST plans/15, the owner 2026-11-07: «во все их нужно встроить FreeDroidWarn»);
        // the content filter keeps every other dependency on Google Maven and Maven Central.
        maven("https://jitpack.io") { content { includeGroup("com.github.woheller69") } }
    }
}
rootProject.name = "KrinikTribit"
include(":app")
