#!/usr/bin/env rake

task :ci => [:dump, :test]

task :dump do
  sh 'vim --version'
end

task :test do
  begin
    sh "bundle exec vim-flavor test"
  rescue
    exit(1)
  end
end
