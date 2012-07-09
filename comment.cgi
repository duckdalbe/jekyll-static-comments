#!/usr/bin/env ruby

# Configuration
emailaddr = 'comments@duckdalbe.org'
subject = 'New comment to moderate'
landingurl = '/static/comment_received.html'
# End of configuration

# TODO: test for required fields and respond helpfully.
# TODO: Make commentform standalone to include here upon failure.
# TODO: commentform field for openpgp-key.
# TODO: commentform field to optionally use name+address from openpgp-key.
# TODO: commentform use JS to disable not usable fields dynamically.
# TODO: Verify OpenPGP-signature and skip moderation upon success.
# TODO: Limit requests per IP per time.

require 'cgi'
require 'mail'
require 'yaml'

@@cgi = CGI.new

def values
  # Read in posted content and escape/sanitize a little.
  values ||= %w(name email link comment).map do |attrb|
    # TODO: test emailaddress, link for validity.
    {attrb => CGI.escape_html(@@cgi[attrb])}
  end
end

def post_id
  post_id ||= @@cgi[post_id]
end

def referer
  referer ||= @@cgi.referer
end

def respond(str_or_header, &block)
  if block_given?
    @@cgi.out(str_or_header) { yield }
  else
    @@cgi.out { str_or_header }
  end
end

def error(str)
  respond("status" => "SERVER_ERROR") { "Error: #{str}" }
end

# Get referred-to post_id and break if invalid.
if ! post_id
  # Something wrong, probably wrong input.
  # TODO: More helpful error message.
  error "error: no post_id.\n#{@@cgi.inspect}"
  exit 1
end

mail = Mail.new
mail.from = emailaddr
mail.to = emailaddr
mail.subject = subject
mail.body = values.to_yaml

mail.delivery_method :sendmail
msg = mail.deliver or error("sending email failed: #{msg.inspect}.\n\nPlease inform the owner of this site!")

if referer.to_s.empty?
  respond "Your browser does not send referrers and thus we can't automatically send you to the appropriate page that thanks you.<br/> Therefor you see only this naked text and will have to use you browser's controls to return to the post.<br/>Oh, and: Thank you for your comment!"
  exit
end

redirecturl = landingurl
respond("status" => "REDIRECT",
        "type" => "text/html",
        "location" => redirecturl) { "<a href='#{redirecturl}'>#{redirecturl}</a>" }
