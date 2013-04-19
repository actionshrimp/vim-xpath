#!/usr/bin/env rake

task :default => [:test_python, :test_vimscript]

task :dump do
  sh 'vim --version'
end

task :test_vimscript do
  begin
    sh "bundle exec vim-flavor test"
  rescue
    exit(1)
  end
end

task :test_python do
  sh "nosetests python"
end
