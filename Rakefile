#!/usr/bin/env rake
#
require 'vim-flavor'

task :default => :test
task :ci => [:dump, :test]

task :dump do
  sh 'vim --version'
end

task :test do
  Vim::Flavor::CLI.start()
end
