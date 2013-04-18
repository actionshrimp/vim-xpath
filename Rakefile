#!/usr/bin/env rake

require 'vim-flavor'

task :default => :test

task :dump do
  sh 'vim --version'
end

task :test do 
  begin
      sh 'vim-flavor test'
  rescue
      exit(1)
  end
end
